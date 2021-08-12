# hcolor
For computing HI-color cross correlations in IllustrisTNG. Depends on hydrotools and pylians

## build
This may change on a user-by-user basis, but files here build a slurm pipeline designed for deepthought2

## output
Where the output is stored

## run
The pipeline that gets built calls these scripts which interact with the library to create the desired output.

## hicc_library
Houses the scripts which determine how the analysis is run, which data is saved, and standardizes the input/output
for each of the steps 