from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from collections import Counter
import re

class WebCourseAnalyzer:
    def __init__(self, url):
        self.url = url
        self.page_content = ""
        self.cleaned_text = ""

    def fetch_content_with_selenium(self):
        # Configure Selenium WebDriver (using Firefox in this example)
        service = Service("geckodriver")  # Ensure geckodriver is in PATH or specify full path
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Firefox(service=service, options=options)

        try:
            driver.get(self.url)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            # Expand all sections if necessary (example for clickable tabs)
            try:
                expandable_elements = driver.find_elements(By.CSS_SELECTOR, ".expandable, .tab, .accordion")
                for element in expandable_elements:
                    ActionChains(driver).move_to_element(element).click(element).perform()
            except Exception as e:
                print(f"Could not expand all sections: {e}")

            self.page_content = driver.page_source
        finally:
            driver.quit()

    def parse_content(self):
        soup = BeautifulSoup(self.page_content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        self.cleaned_text = soup.get_text(separator=" ")

    def extract_titles(self):
        soup = BeautifulSoup(self.page_content, 'html.parser')
        titles = [header.get_text(strip=True) for header in soup.find_all(re.compile('^h[1-6]$'))]
        return titles

    def extract_keywords(self, num_keywords=10):
        words = re.findall(r'\b\w{4,}\b', self.cleaned_text.lower())
        common_words = Counter(words).most_common(num_keywords)
        return [word for word, count in common_words]

    def generate_summary(self, num_sentences=5):
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)\s', self.cleaned_text)
        return ' '.join(sentences[:num_sentences])

    def extract_quizable_info(self):
        potential_questions = []
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)\s', self.cleaned_text)
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ["define", "explain", "what", "how", "why"]):
                potential_questions.append(sentence)
        return potential_questions

    def analyze_full_page(self):
        analysis = {
            "titles": self.extract_titles(),
            "keywords": self.extract_keywords(),
            "summary": self.generate_summary(),
            "quiz_questions": self.extract_quizable_info(),
            "practices": self.generate_practices()
        }
        return analysis

    def generate_practices(self):
        keywords = self.extract_keywords(5)
        practices = [
            f"Define the following terms: {', '.join(keywords)}.",
            "Create a summary of the main points discussed on the page.",
            "Draw a concept map linking the key ideas from the content."
        ]
        return practices

if __name__ == "__main__":
    url = input("Enter the URL of the course page: ")
    analyzer = WebCourseAnalyzer(url)

    try:
        analyzer.fetch_content_with_selenium()
        analyzer.parse_content()

        analysis = analyzer.analyze_full_page()

        print("\n1. Titles and Headings:")
        print(analysis["titles"])

        print("\n2. Keywords:")
        print(analysis["keywords"])

        print("\n3. Summary:")
        print(analysis["summary"])

        print("\n4. Potential Quiz Questions:")
        print(analysis["quiz_questions"])

        print("\n5. Suggested Practices:")
        print(analysis["practices"])

    except Exception as e:
        print(f"An error occurred: {e}")