
import os


save_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    '..', '..', '..', 'experiments', 
    'quant_strategies'
))
os.makedirs(save_dir, exist_ok=True)

print(f"Save directory created at: {save_dir}")
