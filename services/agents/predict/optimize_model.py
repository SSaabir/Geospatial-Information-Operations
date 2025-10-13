"""
Optimize and reduce ML model size using joblib compression
Compatible with scikit-learn DecisionTree or similar models
"""

import joblib
import os
from pathlib import Path

def get_file_size_mb(filepath):
    """Get file size in MB"""
    return os.path.getsize(filepath) / (1024 * 1024)

def optimize_decision_tree_model(model_path):
    """
    Optimize Decision Tree or sklearn-compatible model by:
    1. Using joblib for loading/saving
    2. Compressing the model file
    """
    print(f"📊 Analyzing {model_path}...")

    try:
        # Load model with joblib
        model = joblib.load(model_path)
        print(f"✅ Loaded model successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

    # Get original size
    original_size = get_file_size_mb(model_path)
    print(f"📏 Original size: {original_size:.2f} MB")

    # Show model info if it is a DecisionTree
    print(f"📋 Model type: {type(model).__name__}")
    if hasattr(model, 'tree_'):
        n_nodes = model.tree_.node_count
        print(f"🌳 Tree nodes: {n_nodes:,}")

    # Save optimized model with joblib compression
    compressed_path = model_path.with_name(model_path.stem + "_optimized.pkl")

    print(f"\n🗜️ Optimizing model...")
    joblib.dump(model, compressed_path, compress=('gzip', 9))  # Maximum compression

    # Get optimized size
    optimized_size = get_file_size_mb(compressed_path)
    savings = (1 - optimized_size / original_size) * 100

    print(f"✅ Optimized size: {optimized_size:.2f} MB")
    print(f"💾 Size reduction: {savings:.1f}%")
    print(f"📁 Saved as: {compressed_path}")

    return compressed_path

def test_optimized_model(original_path, optimized_path):
    """Test that optimized model loads correctly"""
    print(f"\n🧪 Testing optimized model...")

    try:
        original_model = joblib.load(original_path)
        optimized_model = joblib.load(optimized_path)

        print(f"✅ Original model type: {type(original_model).__name__}")
        print(f"✅ Optimized model type: {type(optimized_model).__name__}")

        if hasattr(original_model, 'n_features_in_'):
            print(f"✅ Number of input features: {original_model.n_features_in_}")

        print(f"✅ Optimized model loaded successfully and is ready to use!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # Locate model file
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
    optimized_path = optimize_decision_tree_model(model_path)

    if optimized_path:
        # Test optimized model
        success = test_optimized_model(model_path, optimized_path)
        if success:
            print("\n" + "="*70)
            print("✅ OPTIMIZATION COMPLETE!")
            print("="*70)
            print(f"\n📝 To use the optimized model:")
            print(f"   import joblib")
            print(f"   model = joblib.load('{optimized_path.name}')")
            print(f"\n💡 The optimized model is fully compatible with the original!")
