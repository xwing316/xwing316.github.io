// ============================================
// games-data.js — Game definitions dataset
// ============================================

const GAMES = [
  {
    id: 'snake',
    title: 'Snake',
    description: 'The classic snake game! Eat food to grow longer, but don\'t hit the walls or your own tail. Simple yet addictive.',
    category: 'classic',
    thumbnail: 'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)',
    file: 'games/snake.html',
    difficulty: 'Easy',
    emoji: '🐍'
  },
  {
    id: 'memory-match',
    title: 'Memory Match',
    description: 'Test your memory by matching pairs of cards. Flip two at a time and find all matching pairs to win!',
    category: 'puzzle',
    thumbnail: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
    file: 'games/memory.html',
    difficulty: 'Easy',
    emoji: '🃏'
  },
  {
    id: 'pong',
    title: 'Pong',
    description: 'The original arcade classic! Challenge a friend in this 2-player paddle game. First to score wins the round.',
    category: 'classic',
    thumbnail: 'linear-gradient(135deg, #3498db 0%, #2980b9 100%)',
    file: 'games/pong.html',
    difficulty: 'Medium',
    emoji: '🏓'
  },
  {
    id: 'flappy-bird',
    title: 'Flappy Bird',
    description: 'Navigate through endless pipes by tapping to flap. Seems easy? Think again! One of the hardest casual games ever.',
    category: 'action',
    thumbnail: 'linear-gradient(135deg, #1abc9c 0%, #16a085 100%)',
    file: 'games/flappy.html',
    difficulty: 'Hard',
    emoji: '🐦'
  },
  {
    id: 'tic-tac-toe',
    title: 'Tic Tac Toe',
    description: 'Classic strategy game against an unbeatable AI. Can you outsmart the computer and force a draw — or even win?',
    category: 'strategy',
    thumbnail: 'linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)',
    file: 'games/tictactoe.html',
    difficulty: 'Easy',
    emoji: '❌'
  },
  {
    id: 'breakout',
    title: 'Breakout',
    description: 'Smash bricks with a bouncing ball and paddle. Clear all the bricks to advance. A timeless arcade favorite!',
    category: 'action',
    thumbnail: 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)',
    file: 'games/breakout.html',
    difficulty: 'Medium',
    emoji: '🧱'
  },
  {
    id: '2048',
    title: '2048',
    description: 'Slide numbered tiles to combine them and reach the elusive 2048 tile. A puzzle that\'s easy to learn, hard to master.',
    category: 'puzzle',
    thumbnail: 'linear-gradient(135deg, #f1c40f 0%, #f39c12 100%)',
    file: 'games/2048.html',
    difficulty: 'Medium',
    emoji: '2048️'
  },
  {
    id: 'space-invaders',
    title: 'Space Invaders',
    description: 'Defend Earth from waves of descending aliens! Shoot fast and dodge enemy fire in this iconic arcade shooter.',
    category: 'action',
    thumbnail: 'linear-gradient(135deg, #2c3e50 0%, #8e44ad 100%)',
    file: 'games/invaders.html',
    difficulty: 'Hard',
    emoji: '👾'
  }
];

// Category metadata for filters
const GAME_CATEGORIES = {
  all:      { label: 'All Games',    icon: '🎮' },
  puzzle:   { label: 'Puzzle',       icon: '🧩' },
  action:   { label: 'Action',       icon: '⚡' },
  strategy: { label: 'Strategy',     icon: '♟️' },
  classic:  { label: 'Classic',      icon: '🕹️' }
};

// Difficulty ranking for sorting
const DIFFICULTY_ORDER = { 'Easy': 1, 'Medium': 2, 'Hard': 3 };