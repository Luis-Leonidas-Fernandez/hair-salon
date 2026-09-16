# Objetivos de reunión de validación

**Versión:** 1.1  
**Estado:** Actualizado post-validación de negocio  
**Fecha:** septiembre de 2026  
**Responsable:** Proyecto Peluquería Sergio  
**Fuente:** Reunión de validación, reglas de negocio, alcance MVP y ADRs aceptados


## Sistema de reservas Peluquería Sergio

Guía de preguntas y resultado de validación para ajustar reglas de negocio antes del diseño final e implementación.

> **Objetivo de la reunión:** validar si el modelo de reservas documentado coincide con la operación real de la peluquería: servicios, horarios, dos peluqueros, clientes, cancelaciones, recordatorios y administración.

## 1. Enfoque recomendado

La reunión debe ser corta y orientada a decisiones. No conviene seguir diseñando pantallas, SQL o lógica de reservas sin confirmar primero las reglas reales del negocio.

| Bloque | Duración sugerida | Propósito |
| --- | --- | --- |
| Explicar flujo propuesto | 10 min | Mostrar cómo se imagina la reserva desde cliente y administración. |
| Validar reglas principales | 20 min | Cerrar servicios, horarios, peluqueros y cancelaciones. |
| Validar operación interna | 10 min | Confirmar roles, permisos, administración y recordatorios. |
| Cierre | 5 min | Registrar decisiones y dudas abiertas. |

## 2. Preguntas puntuales

### 1. Servicios
- ¿Cuáles son los servicios iniciales?
- ¿Cada servicio tiene duración fija o puede variar?
- ¿El precio se muestra al cliente antes de reservar?
- ¿Hay servicios que solo puede hacer un peluquero específico?
- ¿Hay servicios combinados, por ejemplo corte + barba?

### 2. Peluqueros y agenda
- Confirmar: ¿son exactamente dos peluqueros al inicio?
- ¿Los dos trabajan los mismos días y horarios?
- ¿Atienden en paralelo o hay recursos compartidos que limitan turnos?
- ¿Un cliente elige peluquero o el sistema asigna automáticamente?
- ¿Qué pasa si un peluquero no trabaja un día puntual?

### 3. Horarios y disponibilidad
- ¿Cuál es el horario semanal real?
- ¿Se trabaja con bloques cada 15, 30 o 60 minutos?
- ¿Hay descanso, almuerzo o pausas entre turnos?
- ¿Se permite reservar para el mismo día?
- ¿Con cuánta anticipación máxima se puede reservar?

### 4. Clientes y login con Google
- ¿El cliente debe iniciar sesión con Google obligatoriamente?
- Además del email de Google, ¿qué datos se piden? ¿Teléfono? ¿Nombre? ¿WhatsApp?
- ¿Puede reservar alguien por teléfono y que el admin cargue el turno manualmente?
- ¿Hay clientes bloqueados o con historial de no asistencia?

### 5. Cancelaciones y cambios
- ¿Hasta cuánto tiempo antes puede cancelar un cliente?
- ¿Puede modificar turno o solo cancelar y volver a reservar?
- ¿Quién puede cancelar: cliente, admin, peluquero?
- ¿Se registra motivo de cancelación?
- ¿Qué estados reales usan? Por ejemplo: pendiente, confirmada, cancelada, atendida, no asistió.

### 6. Recordatorios
- ¿Quieren recordatorio automático?
- ¿Por qué canal: email, WhatsApp o ambos?
- ¿Cuánto antes del turno?
- Si falla el envío, ¿la reserva sigue válida? Recomendación técnica: sí.

### 7. Administración
- ¿Quién administra servicios, horarios y precios?
- ¿El admin también puede crear reservas manuales?
- ¿Los peluqueros pueden ver solo su agenda o toda la agenda?
- ¿Los peluqueros pueden cambiar estados de turnos?

### 8. Integraciones futuras
- ¿Necesitan Google Calendar desde el MVP?
- ¿Necesitan WhatsApp desde el MVP o puede quedar para después?
- ¿Van a cobrar seña o pago online? Si sí, eso cambia el alcance.

## 3. Resultado esperado de la reunión

- Lista cerrada de servicios iniciales con duración y precio visible o interno.
- Horarios reales de atención y reglas de disponibilidad por peluquero.
- Decisión sobre si el cliente elige peluquero o si el sistema/admin asigna.
- Política confirmada de cancelación, modificación y no asistencia.
- Datos mínimos del cliente además del login con Google.
- Decisión sobre recordatorios y canal preferido.
- Definición de qué queda dentro del MVP y qué se posterga.

## 4. Resultado registrado

### Decisiones aceptadas

- Servicios iniciales: barbería y peluquería.
- Duración operativa: una hora por cliente.
- Bloques de agenda: 30 minutos.
- Horario general: lunes a sábado, de 9:30 a 22:00.
- Los dos profesionales trabajan en paralelo, cada uno en su puesto.
- El cliente puede elegir peluquero.
- Si un peluquero no trabaja un día puntual, se bloquea su disponibilidad.
- Se permite reservar para el mismo día.
- Anticipación máxima: un mes.
- Login con Google obligatorio.
- Datos adicionales del cliente: nombre, teléfono, WhatsApp y fecha de nacimiento.
- El administrador puede cargar reservas manuales tomadas por teléfono.
- La cancelación puede realizarla cliente, administrador o peluquero.
- Límite de cancelación del cliente: hasta una hora antes del turno.
- El cliente puede modificar el turno.
- La reserva sigue siendo válida aunque falle una notificación.
- Google Calendar queda contemplado para el MVP como integración derivada.

### Decisiones que requieren normalización técnica

Los estados mencionados por el negocio fueron: agendado, reservado, confirmado, asiste, no asistió, pendiente y en espera. No conviene copiarlos sin análisis porque algunos pueden representar estados equivalentes o transiciones operativas. Para implementación se propone un catálogo normalizado y controlado en el modelo físico.

### Pendientes

- Definir proveedor, costo y factibilidad de WhatsApp antes de incluirlo como canal obligatorio.
- Confirmar si los descansos deben configurarse como bloqueos automáticos o manuales, porque la respuesta fue que dependen de la cantidad de clientes.

### Fuera de alcance por ahora

- Pagos, señas y facturación automática. Aunque se mencionó seña para peluquería, no se incorpora todavía al alcance técnico.

## 5. Recomendación final

La validación confirma que ya se puede ajustar documentación y ADRs, pero no conviene implementar pagos ni WhatsApp obligatorio todavía. Las reglas aceptadas deben incorporarse al modelo y las dudas pendientes deben quedar visibles para no transformarlas en supuestos falsos.
