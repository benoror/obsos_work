> [!INFO] `Tasks` from [Meetings/\*\*/\*](file://./Meetings) & [[Tracker]]

---
```tasks
NOT DONE
(folder INCLUDES Meetings) OR (filename INCLUDES Tracker.md)

SORT BY function task.priority, task.file.folder, task.created.format("YYYY[%%]-MM[%%] MMM [- Week] WW")

GROUP BY function task.priorityNameGroupText
GROUP BY function task.file.folder.slice(0, -1).split('/').pop() + '/'
GROUP BY function task.file.filename

SHOW TREE
```
