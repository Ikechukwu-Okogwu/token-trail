This directory is to store datasets to test the similarity detection algorithm. Each subfolder is a repository defined in the phase 3 document. The definition is pasted at the end of this file for convenience

Each repository focuses on testing one aspect of the similarity detection algorithm.

e.g. "Only change variable names JAVA", "Use while loop instead of for loop CPP"

Each repository serves as an optimization goal for a certain aspect of the algorithm.

Todo: Write the test script that:
1. accept such repository
2. create course/assignment and submit all student files in the repository on a running project instance on docker
3. obtain the result from api
4. remove the data uploaded for this test(optional)
5. store the result in localtest/result_log.

In addition to the Repository structure specified in the 

========================

## Repository
This refers to how a complete repository is to be organized. This having application to exporting a repository or submitting a repository to the system. A repository is generally a zip of zip files representing submissions. A submission in this context would be a zip file named appropriately with the identifying information.

E.g. Consider a repository called “LastYearsCourse.zip”, which contains several student submissions: StudentA.zip, StudentB.zip etc.

Upon submission, the system unpacks LastYearsCourse.zip, and adds the contents to the data base with encrypted identification of StudentA, StudentB etc. Note, the upload would already have the Key, since we expect that this repository would be directly associated with an assignment. 

To export, the opposite would take place. All student submissions belonging to the Assignment Key would be zipped, with each student.zip named with the unencrypted Submission ID.