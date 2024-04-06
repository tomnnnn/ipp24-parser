---
geometry: margin=2cm
---
Implementační dokumentace k 1. úloze do IPP 2023/2024\
Jméno a příjmení: Hai Phong Nguyen\
Login: xnguye28\

The parse script is made of two main modules, lexer and parser. The lexer module provides `TokenIterator` class, which generates `Token` objects from a given input file. Token types are determined using regular expressions. If a type cannot be determined a lexical error is thrown. Thanks to the seperation of lexer into two classes, the `TokenIterator` acts as an interface and in case of need, the token detection logic can be easily changed without the need of altering `TokenIterator`.

The parser uses a finite state machine to control the flow of parsing process. Therefore, a State design pattern was used to seperate specific state logic into individual classes. 
An abstract `State` class was implemented. Classes, that implement state specific logic all inherit from this abstract class. The main `Parser` class holds the current `State` object. It also holds data, that is accessible to all state objects. The `State` instances can access the shared data using the `context` attribute, which is set within instantiation. The `parse` method calls `State` handle methods in a cycle, until and end state has been reached.


For syntax check, `OperandReference` class is implemented. Each instance has a method for comparing a given operands list against a set reference arrangement. The method returns the operand types modifications based on the arrangement they are used in.

The initial state `Header` state checks whether a correct header ".IPPcode24" was used.

The syntax check happens in the `SetContext` state, which holds a private dictionary attribute, containing [opcode, `OperandReference`] entries. Upon calling its `handle` method, operation code is extracted from the current `token_buffer` and is used to choose the corresponding `OperandReference` from the dictionary. An operand check is then performed and upon success, the type modifications are applied.

`InstrBuild` state takes the current `token_buffer` and appends a new XML element to the `output_root` ElementTree.

`Print` state prints the built XML tree to stdout.

The State design pattern allows easier code maintance and future modfications, such as adding or removing states from the finite state machine as everything is encapsulated in seperate classes and methods.

```{=latex}
\begin{center}
```

![Parser finite state machine](doc_imgs/fsm.svg "Parser finite state machine"){width=50%}

```{=latex}
\end{center}
```

```{=latex}
\begin{center}
```

![Parser module class diagram](doc_imgs/parser_class_dia.svg "Parser module class diagram"){ width=70% }

```{=latex}
\end{center}
```
