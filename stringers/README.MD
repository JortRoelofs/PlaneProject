# How to define stringers

Stringers contain the following properties:

`name`  
`area`  
`centroid_x`  
`centroid_z`  
`moi_xx`  

the property `name` is used to identify the stringer. Any wing box section referencing to this stringer will use the 
value of `name`. Therefore, it is not recommended to define multiple stringer types with the same name, as this leads 
to undefined behaviour.

The other properties can be written down as functions. In order for this to work, the function must be written in 
Python syntax. `area`, `centroid_x` and `centroid_z` can all be functions based on variables `w`, `h` and `t` for the 
width, height and thickness of stringer respectively. The function of `moi_xx` also allows use of the variables for 
the `area` as `a` and the `centroid_z` as `z`. This is useful for the parallel axis theorem.

By default, all stringers defined in this directory are loaded into the program, as long as the file has the extension 
`.stri`.