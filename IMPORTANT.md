# Important: Input Method

## ⚠️ Only type "1" — never press Enter!

Claude Code approval prompts **complete the selection automatically as soon as "1" is typed**.

Pressing Enter is treated as sending a message, which causes unintended behavior.

```
✅ Correct: type "1" only
❌ Wrong: "1" + Enter
```

## Modified files

- `simple_auto_approver.py`: updated to type "1" only
  - Lines 161-165: main approval logic
  - Lines 180-184: PyCharm tab traversal logic

## Note

All auto-approval logic in this project is implemented to type only the "1" key and never press Enter.
