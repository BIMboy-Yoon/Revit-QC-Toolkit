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
10. Compact Summary
11. Portfolio Display Truncation (25 characters)
12. Review Group Summary (3 samples per group)
13. Review Item Samples (maximum 8)
14. Full CSV Export
15. Summary CSV Export
16. Git Version Control
17. Rollback Workflow

Full CSV에는 모든 상세 Issue를 저장하고, Summary CSV에는 Category, Item Type,
QC Item, Issue Message 기준으로 그룹화한 Count와 Sample Items를 저장합니다.
pyRevit Output에만 Sample Items의 25자 축약 및 그룹당 3개 제한을 적용합니다.
Compact Summary는 검사 수량, Review Item, Issue Group, QC Status와 Export 구성을 표시합니다.
