# frequency_list_from_srt_txt

A Flask web app that parses Japanese `.srt` or `.txt` subtitle files (and optionally a JSON word list) to generate a frequency‐sorted vocabulary list. Includes options to:

- Ignore text in parentheses `( … )`
- Filter out non-word tokens (pure punctuation or symbols, including “・”)
- Exclude numbers and romaji
- Skip words you already know (via an uploaded Migaku Export JSON word list)
- Click any word in the resulting list to see every sentence or subtitle line where it appears

## Installation
1.	Clone the repository to your local machine and navigate into the project folder.
2.	In the terminal create and activate a Python virtual environment:
On macOS/Linux
  ```sh
  python3 -m venv .venv
  source .venv/bin/activate
  ```
On Windows
  ```sh
  python3 -m venv .venv
  .\.venv\Scripts\activate
  ```
3.	Install dependencies by running
  ```sh
  pip install -r requirements.txt
  ```

## Usage
1.	With your environment activated, start the Flask server by running
  ```sh
  python app.py
  ```
2.	Open a browser and navigate to http://127.0.0.1:5000.
3.	On the upload page:
	•	Click Choose .srt or .txt files and select one or more subtitle/text files.
	•	(Optional) Click: Upload JSON of known words and choose a Migaku JSON word list to exclude.
	•	Check the boxes for any filters you want:
	•	Ignore text in parentheses: removes anything inside ().
	•	Filter out non-word tokens: removes punctuation or standalone ・.
	•	Exclude numbers and romaji: removes tokens made of only ASCII letters or digits.
	•	Click Process.
4.	After processing, you will see a list of words with their frequencies. Click on any word to view all occurrences (sentences or subtitle lines), grouped by filename.
5.	To start a new analysis, use the ← Back to Upload link at the bottom of any page.

## License

This project is provided as-is under the MIT License. Feel free to customize and use it for your language-learning purposes.
