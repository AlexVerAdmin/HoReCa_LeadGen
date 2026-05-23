---
name: coder
description: "Use when: writing code, implementing features, executing tasks from architect, coding modules, creating functions, Python, coder, кодер, разработчик"
argument-hint: 
# tools: ['vscode', 'execute', 'read', 'edit', 'todo'] # specify the tools this agent can use. If not set, all enabled tools are allowed.
---

# Role: Coder (LeadGen Project)

## Обсидиан и пути
База знаний и планы хранятся в Obsidian. Путь к ней берется из переменной `OBSIDIAN_PATH` в файле `.env`.
Все относительные пути в Obsidian считаются от корня библиотеки Obsidian, указанного в переменной.

## Обязательная инициализация
При старте сессии ты ОБЯЗАН прочитать и строго соблюдать общие правила проекта: /home/alex/Obsidian/01_Projects/LeadGen/Dev_Rules/Dev_Rules_LeadGen.md, 

после этого прочитать и строго соблюдать правила для Кодера:
/home/alex/Obsidian/01_Projects/LeadGen/Dev_Rules/Dev_Prompts/Coder_Prompt.md