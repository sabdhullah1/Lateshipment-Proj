# Project for Lateshipment
## Population Visualization using MySQL and Python

#### Problem Statement:
Create a MySQL table with following columns,
 * name
 * birthdate
 * deathdate

Given a list of people in MySQL with their birth and end years write a program to fetch rows from MySQL and find the year with the highest population

#### Solutions proposed
 This solution is designed with two modules
  * Module-1: Python script to automatically populate 1 million (adjustable) records into the database. The columns created are
   1. id - unique id
   2. name - a random name chose from among 2.6 lakh names got from the internet (based on names.csv)
   3. sex - male or female (based on names.csv)
   4. birthdate - random uniformly distributed date between 1-1-1900 and 31-12-1999
   5. deathdate - random date generated using birthdate and lifespan, which is random generated value between 0 and 30,000 days

  * Module-2: Visualization framework using Python dash. This framework provides graphs for number of births, number of deaths in a year and also the population across different dates based on the settings provided in the dropdown. There is also a subgraph which provides more details on the hovered point for detailed analysis. Please find the demo below.

#### Demo
[link text](https://www.youtube.com/watch?v=4WwjekbILZI&feature=youtu.be)
