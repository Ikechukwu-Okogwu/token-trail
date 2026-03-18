localtest module is a set of scripts to automatically test the analysis function.
Please follow the following steps to run a complete test:

0.run the token-trail project on docker, make sure http://localhost:8000/docs#/ is available
1.run setup_assignment.py
2.check the recently created file in the folder result_log/, find the assignment id
3.open run_analysis_on_specified_assignment.py, find the variable assignment_id, set its value to the assignment id obtained from the previous step
4.run run_analysis_on_specified_assignment.py. you can find the test result in result_log/