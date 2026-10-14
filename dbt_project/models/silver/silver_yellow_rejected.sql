-- Auditoría: filas descartadas con su causa. Permite revisar y revertir decisiones.
select * from {{ ref('int_yellow_trips_flagged') }}
where reject_reason is not null
