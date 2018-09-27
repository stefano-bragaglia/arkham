# FOIL

## AIMA3e
__function__ Foil(_examples_, _target_) __returns__ a set of Horn clauses  
&emsp;__inputs__: _examples_, set of examples  
&emsp;&emsp;&emsp;&emsp;&emsp;_target_, a literal for the goal predicate  
&emsp;__local variables__: _clauses_, set of clauses, initially empty  

&emsp;__while__ _examples_ contains positive examples __do__  
&emsp;&emsp;&emsp;_clause_ &larr; New-Clause(_examples_, _target_)  
&emsp;&emsp;&emsp;remove positive examples covered by _clause_ from _examples_  
&emsp;&emsp;&emsp;add _clause_ to _clauses_  
&emsp;__return__ _clauses_  

---
__function__ New-Clause(_examples_, _target_) __returns__ a Horn clause  
&emsp;__local variables__: _clause_, a clause with _target_ as head and an empty body  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;_l_, a literal to be added to the clause  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;*extended_examples*, a set of examples with values for new variables  

&emsp;*extended_examples* &larr; _examples_  
&emsp;__while__ *extended_examples* contains negative examples __do__  
&emsp;&emsp;&emsp;_l_ &larr; Choose-Literal(New-Literals(_clause_), *extended_examples*)  
&emsp;&emsp;&emsp;append _l_ to the body of _clause_  
&emsp;&emsp;&emsp;*extended_examples* &larr; set of examples created by applying Extend-Example  
&emsp;&emsp;&emsp;&emsp;to each example in *extended_examples*  
&emsp;__return__ _clause_  

---
__function__ Extend-Example(_example_, _literal_) __returns__ a set of examples  
&emsp;__if__ _example_ satisfies _literal_  
&emsp;&emsp;&emsp;__then return__ the set of examples created by extending _example_ with  
&emsp;&emsp;&emsp;&emsp;each possible constant value for each new variable in _literal_  
&emsp;__else return__ the empty set  

---
__Function ??__ Sketch of the Foil algorithm for learning sets of first-order Horn clauses from examples. New-Literals and Choose-Literal are explained in the text.