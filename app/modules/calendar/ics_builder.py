"""RFC 5545 compliant iCalendar string generator for staff agenda (ADR-018, CU-012)."""

from datetime import UTC, datetime, timedelta

from app.modules.services.shared.domain_types import BookingStatus
from app.modules.services.shared.models import Booking, User


def _format_ics_datetime(dt: datetime) -> str:
    """Convierte un datetime a formato UTC compacto YYYYMMDDTHHMMSSZ."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _escape_ics_text(text: str | None) -> str:
    """Escapa caracteres reservados según RFC 5545 §3.3.11."""
    if not text:
        return ""
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\n", "\\n")


def _fold_line(line: str) -> str:
    """Divide líneas mayores a 75 bytes según RFC 5545 §3.1."""
    if len(line.encode("utf-8")) <= 75:
        return line
    lines: list[str] = []
    current = ""
    for char in line:
        if len((current + char).encode("utf-8")) > 75:
            lines.append(current)
            current = " " + char
        else:
            current += char
    if current:
        lines.append(current)
    return "\r\n".join(lines)


def build_hairdresser_ics_feed(
    hairdresser: User,
    bookings: list[Booking],
    salon_name: str = "After Look",
    salon_address: str = "Avenida Vélez Sarsfield 854",
) -> str:
    """Construye un documento iCalendar RFC 5545 con reservas del peluquero."""
    cal_name = _escape_ics_text(f"{salon_name} - {hairdresser.nombre_completo}")
    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//{salon_name}//Agenda Staff v1.0//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{cal_name}",
        "X-WR-TIMEZONE:America/Argentina/Buenos_Aires",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
    ]

    now_utc_str = _format_ics_datetime(datetime.now(UTC))

    for b in bookings:
        uid = f"booking-{b.id}@afterlook.com"

        dtstart_val = getattr(b, "fecha_hora_inicio", getattr(b, "fecha_inicio", None))
        dtend_val = getattr(b, "fecha_hora_fin", getattr(b, "fecha_fin", None))
        if dtend_val is None and dtstart_val is not None:
            duracion = getattr(b, "duracion_minutos", 60)
            dtend_val = dtstart_val + timedelta(minutes=duracion)

        dtstart = _format_ics_datetime(dtstart_val)
        dtend = _format_ics_datetime(dtend_val)

        cliente_nombre = b.cliente.nombre if getattr(b, "cliente", None) else "Cliente"
        servicio_nombre = (
            b.servicio.nombre if getattr(b, "servicio", None) else "Servicio"
        )
        summary = f"{servicio_nombre} - {cliente_nombre}"

        description_parts = [
            f"Cliente: {cliente_nombre}",
        ]
        if getattr(b, "cliente", None) and getattr(b.cliente, "telefono", None):
            description_parts.append(f"Teléfono: {b.cliente.telefono}")
        if getattr(b, "cliente", None) and getattr(b.cliente, "whatsapp", None):
            description_parts.append(f"WhatsApp: {b.cliente.whatsapp}")

        notas = getattr(b, "notas", getattr(b, "notas_cliente", None))
        if notas:
            description_parts.append(f"Notas: {notas}")
        description_parts.append(f"Estado en salón: {b.estado}")

        description = "\\n".join(_escape_ics_text(p) for p in description_parts)

        status_ics = (
            "CANCELLED"
            if b.estado in (BookingStatus.CANCELLED.value, "CANCELADA", "CANCELLED")
            else "CONFIRMED"
        )

        event_lines = [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_utc_str}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{_escape_ics_text(summary)}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{_escape_ics_text(salon_address)}",
            f"STATUS:{status_ics}",
            "END:VEVENT",
        ]
        lines.extend(event_lines)

    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold_line(line) for line in lines) + "\r\n"
