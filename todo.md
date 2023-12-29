- [ ] 1:1 Minimax
  - [x] Figure out the right scoring method for alpha-beta pruning
    * It needs to be zero sum, but it doesn't need to be monotonic
    * If I'm trying to maximize the score, then maybe this bit ordering: `I'm alive | You're dead`. This will reward me for staying alive, and maybe killing you. It will reward you for killing me, and maybe staying alive (pessimistic about kamakazi snakes).
- [ ] Iterative deepening
- [ ] Alpha Beta pruning
- [ ] Replace other snakes with hazards
- [ ] Snake hazards decay over time
- [ ] Non-considered snakes create a "cloud"
- [ ] Work on non-minimax heurisitcs? Tuning?
- [ ] Profit?