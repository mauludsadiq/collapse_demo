# scenarios.py

SCENARIOS = {
    "budget_approval": [
        ["Alice", "Bob", "Charlie"],   # Step 1: subject
        ["emailed", "called"],         # Step 2: verb
        ["Bob", "him"],                # Step 3: object
        ["and", "but"],                 # Step 4: connector
        ["told", "informed"],           # Step 5: second verb
        ["him", "her"],                 # Step 6: second object
        ["that"],                       # Step 7: complementizer
        ["the", "a"],                   # Step 8: article
        ["budget", "report"],           # Step 9: noun
        ["was", "is"],                   # Step 10: auxiliary
        ["approved", "denied"],         # Step 11: participle
        ["."],                          # Step 12: punctuation
    ],

    "coref": [
        ["She", "He", "They"],          # Step 1: pronoun
        ["presented", "presents"],      # Step 2: verb
        ["the", "a"],                   # Step 3: article
        ["results", "budget", "report"],# Step 4: noun
        [".", "!"],                     # Step 5: punctuation
    ],

    "tense_shift": [
        ["The", "A"],                   # Step 1: article
        ["meeting", "conference"],      # Step 2: noun
        ["starts", "started"],          # Step 3: verb
        ["yesterday", "tomorrow"],      # Step 4: time marker
        [".", "!"],                     # Step 5: punctuation
    ],

    "domain_kb": [
        ["The"],                        # Step 1: article
        ["formula", "equation"],        # Step 2: noun
        ["equals", "is"],               # Step 3: verb
        ["E=mc^2", "2+2=4"],            # Step 4: fact
        [".", "!"],                     # Step 5: punctuation
    ],
}
