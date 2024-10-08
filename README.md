# Convo: a conversational programming language

Convo is a high-level, conversational programming language designed to be generated and interpreted by Large Language Models (LLMs). It allows developers to write code in plain, natural language, making programming more accessible and intuitive. You can think of Convo as high-level pseudocode that describes the "gist" of a program, which a LLM can then translate into specific programming languages like Python, JavaScript, or any other language.

The flow for creating a convo app is `english->convo->python`. Why is that better then the current flow of `english->python`? When you ask ChatGPT to "create a snake game using python" you can't predict what version of snake you're going to get back from the model. It will be a version of snake but you don't know what features it's going to have, how it will be styled, etc.  When you ask ChatGPT to "create a snake game using convo" you're also going to get back a version of snake with an unpredictable set of features, but it's written at a much higher level and using natural language. You can easily tweak the convo version of the app to have the features and styling you want and then once you get the convo program the way you want you can send it to the model to generate a python version of the game. The returned output will be much cloaser to having all of the styling and features you specified in your convo program. 

> [!NOTE]  
> It's important to note that there is no special program or application needed to use Convo. It's just a prompting technique. 
> In fact there's a [Convo GPT](https://chatgpt.com/g/g-AL8dpM0dQ-convo) that will guide you through the entire process of creating a convo program and then porting that to a target language.

## Table of Contents

1. [Key Features](#key-features)
2. [Snake Game Example](#snake-game-example)
3. [Advantages of Convo](#advantages-of-convo)
4. [Full Specification and Examples](#full-specification-and-examples)
5. [Creating Convo Programs](#creating-convo-programs)
   - [Generating Convo Programs](#generating-convo-programs)
   - [Porting Convo Programs to other Languages](#porting-convo-programs-to-other-languages)
6. [Origins and Why Convo Works](#origins-and-why-convo-works)

## Key Features

- **Natural Language Syntax**: Write code using everyday language, making it easy to read and understand.
- **Multilingual Support**: Write Convo programs in any language, not just English, allowing for global accessibility. See: [snake in Spanish](examples/snake-es.convo)
- **Implicit Variable Declaration**: Variables are created when first mentioned, reducing the need for explicit declarations.
- **Flexible Control Structures**: Use natural phrases like "If", "While", "For each" to control the flow of the program.
- **Functions and Procedures**: Define and call functions using plain language descriptions.
- **Object-Oriented Concepts**: Define classes and objects using descriptive language, enabling intuitive OOP features.
- **Error Tolerance**: Minor grammatical errors are tolerated, with the LLM inferring the intended meaning.
- **Style and Resource Definitions**: Organize styles and resources in dedicated sections for better organization.

## Snake Game Example

Below is an example of how you might write a simple Snake game in Convo:

```plaintext
Section: Game Setup

Create a grid with 20 rows and 20 columns.
Create a snake starting at the center of the grid with a length of 3.
Set the initial direction of the snake to "right".
Place a food item randomly on the grid.

Section: Game Loop

While the game is running,
    Display the grid with the snake and food.
    Ask the user for the direction (up, down, left, right).
    If the direction is valid, then
        Update the snake's direction to the user's input.
    Move the snake in the current direction.
    If the snake eats the food, then
        Increase the snake's length by 1.
        Place a new food item randomly on the grid.
    If the snake collides with itself or the wall, then
        End the game and display "Game Over! Your score is [snake's length]."

Section: Functions

To display the grid with the snake and food,
    Clear the screen.
    For each cell in the grid,
        If the cell contains a part of the snake, then
            Display "S".
        Else if the cell contains food, then
            Display "F".
        Else
            Display ".".

To move the snake in the current direction,
    Calculate the new head position based on the current direction.
    Add the new head position to the snake.
    Remove the last part of the snake unless it has just eaten food.

To place a food item randomly on the grid,
    Choose a random empty cell on the grid.
    Place the food item in that cell.
```

### Explanation

1. **Game Setup:**
   - A grid is created to represent the game area, and a snake is initialized at the center with a length of 3.
   - The initial direction of the snake is set to "right", and a food item is placed randomly on the grid.

2. **Game Loop:**
   - The game runs in a loop, continuously displaying the grid and asking the user for input to change the snake's direction.
   - The snake moves in the current direction, and if it eats the food, its length increases, and a new food item is placed.
   - The game ends if the snake collides with itself or the wall, displaying a "Game Over" message with the score.

3. **Functions:**
   - `Display the grid with the snake and food`: This function clears the screen and displays the current state of the grid, showing the snake and food.
   - `Move the snake in the current direction`: This function updates the snake's position based on its current direction and handles the growth of the snake when it eats food.
   - `Place a food item randomly on the grid`: This function selects a random empty cell to place a new food item.

## Advantages of Convo

- **Write Once, Run Anywhere**: Write Convo programs in any natural language, and LLMs can interpret and generate code in various programming languages.
- **Future-Proof Code**: As LLMs improve over time, you can regenerate the underlying implementation code from your Convo programs without changing the original code.
- **Accessibility**: Lowers the barrier to programming by allowing people to use language they are comfortable with.
- **Leverage AI Improvements**: Benefit from advancements in AI to produce more efficient and sophisticated code over time.

## Full Specification and Examples

For a complete overview of Convo's syntax and features, refer to the [full Convo specification](convo-spec.md). If you'd like to create your own custom GPT you can view the source for the default [Convo GPT Instructions](gpt-instructions.md). 

## Creating Convo Programs

You can easily create new convo programs using a tool like [ChatGPT](https://chatgpt.com/) or [Claude](https://claude.ai/). The [Examples](https://github.com/Stevenic/convo/tree/main/examples) folder contains a small set of example .convo files and the .html & .py files they ported to.  There's also a [Convo GPT](https://chatgpt.com/g/g-AL8dpM0dQ-convo) that will guide you through creating a convo program and then porting that to a target language.

### Generating Convo Programs

Generating a convo program is as simple as creating a prompt that describes the program you want and then appending the text of the [convo spec](convo-spec.md) to your prompt:

![create convo app](images/create-convo-app.png)

![generated convo app](images/generated-convo-app.png)

Once you've generated your base program definition you can tweak it and make changes either using generative AI or directly using natural language.

### Porting Convo Programs to other Languages

Convo programs can be easily ported to other languages like Python or JavaScript. Just create a prompt specifying the language to port the program to and then paste in the program.  The LLM will intuitively figure out the right code to generate using just the program definition so no spec is needed during this phase.  You can also express any style modifications or implementation details to use during this phase like specific libraries to use:

![port convo app](images/port-convo-app.png)

![ported convo app](images/ported-convo-app.png)

Save the ported app to your environment of choice to run it.  More advanced programs will likely require some debugging and you can use generative AI tools like Canvas to help with this debugging.

## Origins and Why Convo Works

Convo was designed by `o1-preview` with a bit of prompting by me. I wanted to know; If the model could design any programming language it wanted to, what would it design? I started by asking the model to list every programming language it could think of and enumerate each languages pro's & cons. I then asked it to select it's favorite language and it chose Python. I'm a TypeScript guy so whatever... I then gave it the prompt "In the future every person on the planet will be a programmer. Thinking about a more conversationally friendly language. What would it's key features be?" The model identified 20 key features of such a language and placed a heavy emphisis on inclusivity and collaboration. I then asked for the basic syntax rules of this new language and that resulted in the first draft of the Convo spec. So why does Convo work?

The Convo spec is interesting and it's an important component but it's really just a plot device. It puts the model in the desired frame of mind to generate [pseudocode](https://en.wikipedia.org/wiki/Pseudocode) when prompted to create a program. Pseudocode, is classically how developers exchange ideas when talking about algorithms and code. Pseudocode is nice because it's language agnostic and naturally fuzzy. Two developers that don't share a programming language in common can still exchange ideas via pseudocode. These models are more about chaining concepts together then they are about chaining specific words or tokens. The concept of a variable is the same for the model regardless of whether it's a variable definied in a specific programming language or a variable defined in pseudocode. The same is true for every other programming construct which is what makes pseudocode an ideal abstraction for describing program definitions to a machine that's, debatably, capable of reasoning like a human.

Pseudocode naturally abstracts away low level implementation details and focuses more on high level logic flows. This results in a reduction of complexity that makes it easier for the model to generate valid pseudocode then valid python or javascript. Arguably, all pseudocode is valid whcih means that every Convo program the model generates is likely to be 100% correct. So the first step of going from `english->convo` always results in a valid program. The second step of going from `convo->python` can result in errors but the chance of generating errors should be reduced. That's because the complexity of the generation task has been reduced.  This reduction of complexity stems from the fact that most of the highlevel program decisions will have been made in the convo program. That frees the model up to simply focus on the low-level implementation details versus having to also make high-level decisions.  The more focused these models are the generally more reliable they are.

The other thing that's maybe not so obvious is that Pseudocode tends to be a more action forward description language. The instruction heavy Pseudocode leans into the instruction tuning these models have undergone. All of these forces combine to yield observably more consitent and generally better program generation.


