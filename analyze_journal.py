import argparse

from daybookml.analysis import analyze_journal, sm_fun

if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    ap.add_argument('journal_file', help="path to journal text file")
    args = vars(ap.parse_args())

    with open(args['journal_file']) as f:
        journal_content = f.read()

    print("[INFO] Analyzing file...")
    ds, ed = analyze_journal(journal_content)

    print("======= Document Sentiment =======")
    print(f"Overall: {ds}")

    print("======== Entity Sentiment =======")

    print("Events:")
    for i in ed['events']:
        print(f'{i[0]}: {sm_fun(i[1], i[2])}')

    print("\nPeople:")
    for i in ed['people']:
        print(f'{i[0]}: {sm_fun(i[1], i[2])}')

    print("\nLocations:")
    for i in ed['locations']:
        print(f'{i[0]}: {sm_fun(i[1], i[2])}')

    print("\nOther:")
    for i in ed['other']:
        print(f'{i[0]}: {sm_fun(i[1], i[2])}')
