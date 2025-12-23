from environments.openspiel.env import Actor
import os
from dotenv import load_dotenv
import asyncio
import random
import json

load_dotenv()

NUM_SAMPLE_PER_GAME = 30
NUM_CONCURRENT = 4
AVAILABLE_GAMES = [
    # Tier 1: Excellent evaluation games (⭐⭐⭐⭐⭐)
    # High trajectory diversity, strong strategic depth, proven evaluation quality
    "goofspiel",        # idx=0:  Bidding strategy, 100% success, 7.8k tokens, high diversity
    "liars_dice",       # idx=1:  Probability reasoning, 100% success, 1.1k tokens ⭐
    "leduc_poker",      # idx=2:  Poker reasoning, 100% success, 1.3k tokens ⭐
    "gin_rummy",        # idx=3:  Card strategy, 100% success, 167.8k tokens (acceptable)
    
    # Tier 2: High-quality evaluation games (⭐⭐⭐⭐)
    # Good trajectory diversity, moderate difficulty, effective evaluation
    "othello",          # idx=4:  Spatial reasoning, 50% success, 105.8k tokens
    "backgammon",       # idx=5:  Long-term planning, 50% success, 347.2k tokens
    "hex",              # idx=6:  Path planning, 100% success, 13.9k tokens
    "clobber",          # idx=7:  Capture tactics, 100% success, 16.9k tokens (FIXED)
    
    # Tier 3: Multi-player & Complex games (⭐⭐⭐⭐)
    # Higher complexity, useful for advanced evaluation
    "hearts",           # idx=8:  4-player card game, 50% success, 27.5k tokens (FIXED)
    "euchre",           # idx=9:  Trump-based card game, 100% success, 5.8k tokens
    "dots_and_boxes",   # idx=10: Spatial control, 100% success, 62.1k tokens
    
    # Tier 4: High-complexity strategy games (⭐⭐⭐⭐)
    # Complex but high token consumption - use for advanced testing
    "go",               # idx=11: Board strategy (5x5/7x7), 50% success, 119.1k tokens (OPTIMIZED)
    "chess",            # idx=12: Complex strategy, 100% success, 287.1k tokens (OPTIMIZED)
    "checkers",         # idx=13: Classic strategy, 100% success, 83.8k tokens
    "quoridor",         # idx=14: Path blocking, 100% success, 38.9k tokens
    
    # Tier 5: Probability & Imperfect Information (⭐⭐⭐)
    # Special category for testing hidden information reasoning
    "blackjack",        # idx=15: Probability reasoning (vs dealer), 50% success, 519 tokens (FIXED)
    "phantom_ttt",      # idx=16: Hidden opponent moves, 100% success, 1.2k tokens (kept for imperfect info testing)
    
    # Tier 6: Single-player games (⭐⭐⭐⭐⭐) - NEW
    # High trajectory diversity, excellent for testing spatial/sequential reasoning
    "2048",             # idx=17: Sliding tile puzzle, spatial planning, ~50-200 steps
    "solitaire",        # idx=18: Card sequencing, shuffled deck (high diversity), ~30-100 steps
]

actor = Actor(api_key=os.getenv("OPENROUTER_API_KEY"))

async def main():
    data = []
    
    async def process_config(game_id, config_id):
        task_id = game_id * 100000000 + config_id
        
        result = await actor.evaluate(
            task_id=task_id,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-5",
            seed=random.randint(0, 1000000),
            opponent="random"
        )
        
        return result
    
    for game_id in range(1000, 1000 + len(AVAILABLE_GAMES)):
        # Process config_ids in batches of 4
        for batch_start in range(0, NUM_SAMPLE_PER_GAME, NUM_CONCURRENT):
            batch_end = min(batch_start + NUM_CONCURRENT, NUM_SAMPLE_PER_GAME)
            print(f"Processing samples {batch_start} to {batch_end} for game {game_id}")
            
            # Create tasks for this batch
            tasks = [
                process_config(game_id, config_id)
                for config_id in range(batch_start, batch_end)
            ]
            
            # Run tasks concurrently
            results = await asyncio.gather(*tasks)
            data.extend(results)
            # save data to json
            with open(f"data.json", "w") as f:
                json.dump(data, f, indent=2)
            print(f"Saved {len(data)} results")
    
    # save data to json
    with open("data.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
	asyncio.run(main())
			
