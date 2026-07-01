# Workflow

1. Codex Prompt
2. pyRevit Script
3. Revit Model Read-only Check
4. Sheet QC
5. View QC
6. Parameter QC
7. Detailed Issue Collection
8. Issue Grouping
9. Full-detail CSV Data Preservation
10. Portfolio Display Truncation
11. Review Group Summary
12. Review Item Samples
13. Full CSV Export
14. Summary CSV Export
15. Git Version Control
16. Rollback Workflow

Full CSV에는 모든 상세 Issue를 저장하고, Summary CSV에는 Category, Item Type,
QC Item, Issue Message 기준으로 그룹화한 Count와 Sample Items를 저장합니다.
pyRevit Output에만 Sample Items와 긴 요소 이름의 35자 축약 규칙을 적용합니다.
