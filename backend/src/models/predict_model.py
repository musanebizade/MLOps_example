import warnings

warnings.filterwarnings("ignore")

import gzip
import os
import pickle

import pandas as pd
from sklearn.metrics import accuracy_score

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def load_model(filepath: str) -> object:
    """
    Function read pickle object and returns model.
    """
    with gzip.open(filepath, "rb") as f:
        p = pickle.Unpickler(f)
        clf = p.load()
    return clf


def main():
    # file_path = os.path.join(ROOT_DIR, "data", "external", "X_test.xlsx")
    X_test = pd.read_excel(os.path.join(ROOT_DIR, "data", "external", "X_test.xlsx"))
    y_test = pd.read_excel(os.path.join(ROOT_DIR, "data", "external", "y_test.xlsx"))

    # Deserialize (load) and test again
    model_path = os.path.join(ROOT_DIR, "models", "titanic_rf.pkl.gz")
    loaded_model = load_model(model_path)
    y_pred_loaded = loaded_model.predict(X_test)
    acc_loaded = accuracy_score(y_test, y_pred_loaded)
    print(f"Test accuracy (after load):  {acc_loaded:.3f}")


if __name__ == "__main__":
    main()
