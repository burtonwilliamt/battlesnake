# Battle Snake
This is a library and collection of snakes to the [battlesnake](https://play.battlesnake.com/) game.


## TODO on fringe:
* Check the correctness of the generated states. Are we exploring everything? Is the simulation correct?
* Add actual results and optimality reasoning
* Reduce branching to increase depth. (Avoid your neck and the walls.)
* If node D is a decendent of node P, and node P is a decision node for snake i that has seen a solution to live for at least t turns, if node D has snake i as dead, and node D is at turn < t then return immediately.
