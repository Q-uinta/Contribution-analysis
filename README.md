# Contribution analysis for PEF/LCA studies 

### Automatized way to create a contribution analysis
This code provides a way to automatically create a contribution analyses for PEF/LCA studies. In this example SimaPro results are imported and the contribution analysis is automatically generated and exported to a csv named output. 

Specifically, it adds to the csv (formatted):
- The impact categories that together contribute to at least 80% of the single score
- The activities that contribute together to at least 80% to the impact category
- The processes that contribute together at least 80% to the impact category (per activity)

An example of the expected output is:

| Impact Category | [%] | Activity | [%] | Process | [%] |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- | 
| Impact cat. 1 | 50% | Activity 3 | 81% | Process 2 | 45% |
| Impact cat. 2 | 40% | Activity 5 | - | Process 1 | 43% |










