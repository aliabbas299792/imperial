from common import DEFAULT_CLEAN_DATASET_PATH, DEFAULT_NOISY_DATASET_PATH, loadRawData
from crossValidate import crossValidateDataset
from visualise import generateVisualisations
import argparse


def main():
    parser = argparse.ArgumentParser(description="Process dataset paths.")

    # Mutually exclusive group for command-line arguments
    groupPaths = parser.add_mutually_exclusive_group(required=True)
    groupPaths.add_argument(
        "--clean", action="store_true", help="Use the clean dataset"
    )
    groupPaths.add_argument(
        "--noisy", action="store_true", help="Use the noisy dataset"
    )
    groupPaths.add_argument("--path", type=str, help="Specify the dataset path")

    groupFunctionality = parser.add_mutually_exclusive_group(required=True)
    groupFunctionality.add_argument(
        "--visualisation",
        action="store_true",
        help="Generate visualisations for the decision tree",
    )
    groupFunctionality.add_argument(
        "--cross_validation",
        action="store_true",
        help="Generate cross validation statistics for the decision tree",
    )

    args = parser.parse_args()

    # Determine which dataset path to use based on command-line arguments
    if args.clean:
        datasetPath = DEFAULT_CLEAN_DATASET_PATH
    elif args.noisy:
        datasetPath = DEFAULT_NOISY_DATASET_PATH
    else:
        datasetPath = args.path

    dataset = loadRawData(datasetPath)

    if args.visualisation:
        generateVisualisations(dataset)
    else:
        crossValidateDataset(dataset)


if __name__ == "__main__":
    main()
