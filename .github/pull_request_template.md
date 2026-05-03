# PR Description

## ¿Qué hace este PR?
<!-- Una frase clara. Ejemplo: "Agrega el cliente de Google Books con retry exponencial." -->

## ¿Por qué?
<!-- Contexto: qué problema resuelve, qué tarea del roadmap atiende -->

## Tipo de cambio
- [ ] feat: nueva funcionalidad
- [ ] fix: corrección de bug
- [ ] refactor: cambio sin alterar comportamiento
- [ ] docs: solo documentación
- [ ] test: solo tests
- [ ] chore: mantenimiento (deps, config)
- [ ] perf: mejora de performance
- [ ] ci: cambios en CI/CD

## Sprint / Issue relacionado
<!-- Cierra #N o relaciona con sprint del CLAUDE.md -->
Cierra #

## Cambios principales
<!-- Bullet points con los cambios clave -->
-
-

## Decisiones tomadas
<!-- Si tomaste alguna decisión arquitectónica, documenta aquí. Si es importante, crea un ADR en docs/adr/ -->

## Cómo probarlo localmente
```bash
# Pasos para reproducir
```

## Checklist (Definition of Done)

- [ ] El código compila y la app arranca
- [ ] `ruff check .` pasa
- [ ] `ruff format --check .` pasa
- [ ] `mypy app/` pasa en strict
- [ ] `pytest` pasa
- [ ] Hay tests nuevos para la lógica agregada
- [ ] Si toca dinero, hay tests de casos límite
- [ ] Si toca servicio externo, hay test con mock
- [ ] Si cambia el modelo, hay migración Alembic revisada
- [ ] `CHANGELOG.md` actualizado si aplica
- [ ] ADR creado si hay decisión arquitectónica nueva
- [ ] PR < 400 líneas modificadas (excl. lockfiles y migraciones)
- [ ] No hay TODOs sin issue asociado
- [ ] No hay `print()`, `console.log`, ni código comentado
- [ ] No se commitearon credenciales

## Screenshots / Logs
<!-- Si aplica -->

## Notas para el revisor
<!-- Algo que Leo deba mirar con atención -->
