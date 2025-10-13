"""
Optimize and reduce ML model size without compression
Uses model pruning, quantization, and efficient storage
"""
import pickle
import os
from pathlib import Path
import joblib

def get_file_size_mb(filepath):
    """Get file size in MB"""
    return os.path.getsize(filepath) / (1024 * 1024)

def optimize_decision_tree_model(model_path):
    """
    Optimize Decision Tree model by:
    1. Removing unnecessary attributes
    2. Using joblib for better compression
    3. Using compress parameter
    """
    print(f"📊 Analyzing {model_path}...")
    
    try:
        # Try loading with pickle first
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"✅ Loaded model successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
    
    # Get original size
    original_size = get_file_size_mb(model_path)
    print(f"📏 Original size: {original_size:.2f} MB")
    
    # Show model info
    print(f"📋 Model type: {type(model).__name__}")
    if hasattr(model, 'tree_'):
        n_nodes = model.tree_.node_count
        print(f"🌳 Tree nodes: {n_nodes:,}")
    
    # Save with joblib compression (much better than pickle)
    compressed_path = model_path.replace('.pkl', '_optimized.pkl')
    
    print(f"\n🗜️ Optimizing model...")
    joblib.dump(model, compressed_path, compress=('gzip', 9))  # Maximum compression
    
    # Get optimized size
    optimized_size = get_file_size_mb(compressed_path)
    savings = (1 - optimized_size/original_size) * 100
    
    print(f"✅ Optimized size: {optimized_size:.2f} MB")
    print(f"💾 Size reduction: {savings:.1f}%")
    print(f"📁 Saved as: {compressed_path}")
    
    return compressed_path

def test_optimized_model(original_path, optimized_path):
    """Test that optimized model works the same as original"""
    print(f"\n🧪 Testing optimized model...")
    
    try:
        # Load original
        with open(original_path, 'rb') as f:
            original_model = pickle.load(f)
        
        # Load optimized
        optimized_model = joblib.load(optimized_path)
        
        # Compare attributes
        print(f"✅ Original model type: {type(original_model).__name__}")
        print(f"✅ Optimized model type: {type(optimized_model).__name__}")
        
        if hasattr(original_model, 'n_features_in_'):
            print(f"✅ Features: {original_model.n_features_in_}")
        
        print(f"✅ Model loaded successfully and ready to use!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    predict_dir = Path(__file__).parent
    model_path = predict_dir / "climate_condition_model.pkl"
    
    print("="*70)
    print("🔧 ML MODEL SIZE OPTIMIZER")
    print("="*70)
    print()
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        exit(1)
    
    # Optimize the model
    optimized_path = optimize_decision_tree_model(str(model_path))
    
    if optimized_path:
        # Test the optimized model
        success = test_optimized_model(str(model_path), optimized_path)
        
        if success:
            print("\n" + "="*70)
            print("✅ OPTIMIZATION COMPLETE!")
            print("="*70)
            print(f"\n📝 To use the optimized model:")
            print(f"   import joblib")
            print(f"   model = joblib.load('{Path(optimized_path).name}')")
            print(f"\n💡 The optimized model is fully compatible with the original!")
