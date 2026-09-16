from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Role(TimestampMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuarios: Mapped[list[User]] = relationship(back_populates="rol")


class User(TimestampMixin, Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    email_google: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    rol_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    rol: Mapped[Role] = relationship(back_populates="usuarios")
    disponibilidades: Mapped[list[Availability]] = relationship(
        back_populates="usuario"
    )
    reservas_como_peluquero: Mapped[list[Booking]] = relationship(
        back_populates="peluquero", foreign_keys="Booking.peluquero_id"
    )
    reservas_como_usuario: Mapped[list[Booking]] = relationship(
        back_populates="usuario_creador", foreign_keys="Booking.usuario_id"
    )
    servicios: Mapped[list[UserService]] = relationship(back_populates="usuario")
    auditorias: Mapped[list[AuditChange]] = relationship(back_populates="realizado_por")
    historiales: Mapped[list[BookingHistory]] = relationship(
        back_populates="realizado_por"
    )


class Client(TimestampMixin, Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    email_google: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado_cuenta: Mapped[str] = mapped_column(
        String(20), default="ACTIVA", nullable=False
    )

    reservas: Mapped[list[Booking]] = relationship(back_populates="cliente")

    __table_args__ = (
        CheckConstraint(
            "estado_cuenta IN ('ACTIVA', 'SUSPENDIDA', 'INACTIVA')",
            name="ck_clientes_estado_cuenta",
        ),
    )


class Service(TimestampMixin, Base):
    __tablename__ = "servicios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo_servicio: Mapped[str] = mapped_column(String(30), nullable=False)
    duracion_minutos: Mapped[int] = mapped_column(default=60, nullable=False)
    precio_base: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal(0), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    reservas: Mapped[list[Booking]] = relationship(back_populates="servicio")
    usuarios: Mapped[list[UserService]] = relationship(back_populates="servicio")

    __table_args__ = (
        CheckConstraint(
            "tipo_servicio IN ('BARBERIA', 'PELUQUERIA')",
            name="ck_servicios_tipo_servicio",
        ),
        CheckConstraint("duracion_minutos > 0", name="ck_servicios_duracion_positiva"),
        CheckConstraint("precio_base >= 0", name="ck_servicios_precio_no_negativo"),
    )


class UserService(TimestampMixin, Base):
    __tablename__ = "usuarios_servicios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    servicio_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("servicios.id", ondelete="RESTRICT"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuario: Mapped[User] = relationship(back_populates="servicios")
    servicio: Mapped[Service] = relationship(back_populates="usuarios")

    __table_args__ = (
        UniqueConstraint("usuario_id", "servicio_id", name="uq_usuario_servicio"),
    )


class Availability(TimestampMixin, Base):
    __tablename__ = "disponibilidades"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    dia_semana: Mapped[int] = mapped_column(nullable=False)
    hora_desde: Mapped[time] = mapped_column(Time, nullable=False)
    hora_hasta: Mapped[time] = mapped_column(Time, nullable=False)
    bloqueo_excepcional: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    motivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuario: Mapped[User] = relationship(back_populates="disponibilidades")

    __table_args__ = (
        CheckConstraint("dia_semana BETWEEN 1 AND 7", name="ck_disponibilidades_dia"),
        CheckConstraint(
            "hora_hasta > hora_desde", name="ck_disponibilidades_rango_horario"
        ),
        Index("ix_disponibilidades_usuario_dia", "usuario_id", "dia_semana"),
    )


class Booking(TimestampMixin, Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False
    )
    servicio_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("servicios.id", ondelete="RESTRICT"), nullable=False
    )
    peluquero_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    usuario_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True
    )
    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    duracion_minutos: Mapped[int] = mapped_column(default=60, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE", nullable=False)
    canal_reserva: Mapped[str] = mapped_column(
        String(20), default="WEB", nullable=False
    )
    precio_estimado: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal(0), nullable=False
    )
    notas_cliente: Mapped[str | None] = mapped_column(Text, nullable=True)

    cliente: Mapped[Client] = relationship(back_populates="reservas")
    servicio: Mapped[Service] = relationship(back_populates="reservas")
    peluquero: Mapped[User] = relationship(
        back_populates="reservas_como_peluquero", foreign_keys=[peluquero_id]
    )
    usuario_creador: Mapped[User | None] = relationship(
        back_populates="reservas_como_usuario", foreign_keys=[usuario_id]
    )
    historial: Mapped[list[BookingHistory]] = relationship(
        back_populates="reserva", cascade="all, delete-orphan"
    )
    notificaciones: Mapped[list[Notification]] = relationship(
        back_populates="reserva", cascade="all, delete-orphan"
    )
    eventos_calendario: Mapped[list[CalendarEvent]] = relationship(
        back_populates="reserva", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "estado IN ("
            "'PENDIENTE', 'EN_ESPERA', 'AGENDADA', 'RESERVADA', "
            "'CONFIRMADA', 'ASISTIO', 'NO_ASISTIO', 'CANCELADA')",
            name="ck_reservas_estado",
        ),
        CheckConstraint(
            "canal_reserva IN ('WEB', 'ADMIN', 'TELEFONO', 'WHATSAPP')",
            name="ck_reservas_canal",
        ),
        CheckConstraint("duracion_minutos > 0", name="ck_reservas_duracion_positiva"),
        CheckConstraint("precio_estimado >= 0", name="ck_reservas_precio_no_negativo"),
        Index("ix_reservas_agenda_peluquero_fecha", "peluquero_id", "fecha_inicio"),
        Index("ix_reservas_cliente_fecha", "cliente_id", "fecha_inicio"),
    )


class BookingHistory(Base):
    __tablename__ = "historial_reservas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reserva_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False
    )
    estado_anterior: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estado_nuevo: Mapped[str] = mapped_column(String(20), nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    realizado_por_usuario_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    reserva: Mapped[Booking] = relationship(back_populates="historial")
    realizado_por: Mapped[User | None] = relationship(back_populates="historiales")


class Notification(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reserva_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    canal: Mapped[str] = mapped_column(String(20), nullable=False)
    destinatario: Mapped[str] = mapped_column(String(254), nullable=False)
    estado_envio: Mapped[str] = mapped_column(
        String(20), default="PENDIENTE", nullable=False
    )
    fecha_programada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fecha_envio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    reserva: Mapped[Booking] = relationship(back_populates="notificaciones")

    __table_args__ = (
        CheckConstraint(
            "canal IN ('EMAIL', 'WHATSAPP', 'SMS')", name="ck_notificaciones_canal"
        ),
        CheckConstraint(
            "estado_envio IN ('PENDIENTE', 'ENVIADA', 'FALLIDA')",
            name="ck_notificaciones_estado_envio",
        ),
        Index("ix_notificaciones_pendientes", "estado_envio", "fecha_programada"),
    )


class CalendarEvent(Base):
    __tablename__ = "eventos_calendario"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reserva_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False
    )
    proveedor: Mapped[str] = mapped_column(
        String(30), default="GOOGLE_CALENDAR", nullable=False
    )
    evento_externo_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado_sync: Mapped[str] = mapped_column(
        String(20), default="PENDIENTE", nullable=False
    )
    ultima_sincronizacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    detalle_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    reserva: Mapped[Booking] = relationship(back_populates="eventos_calendario")

    __table_args__ = (
        UniqueConstraint(
            "reserva_id", "proveedor", name="uq_evento_calendario_reserva_proveedor"
        ),
        CheckConstraint(
            "estado_sync IN ('PENDIENTE', 'SINCRONIZADO', 'FALLIDO', 'CANCELADO')",
            name="ck_eventos_calendario_estado_sync",
        ),
    )


class AuditChange(Base):
    __tablename__ = "auditoria_cambios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entidad_tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    entidad_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    accion: Mapped[str] = mapped_column(String(30), nullable=False)
    datos_anteriores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    datos_nuevos: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    realizado_por_usuario_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    realizado_por: Mapped[User | None] = relationship(back_populates="auditorias")

    __table_args__ = (Index("ix_auditoria_entidad", "entidad_tipo", "entidad_id"),)
