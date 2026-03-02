#!/bin/bash
# IndexNow submission script for N3X1S blog
# Submits all URLs to Bing, Yandex, Seznam.cz, Naver

KEY="acbf345155724b62b20c40541d78191c"
HOST="maxkle1nz.github.io"
KEY_LOCATION="https://maxkle1nz.github.io/n3x1s-blog/${KEY}.txt"

# All URLs from sitemap
URLS=(
"https://maxkle1nz.github.io/n3x1s-blog/"
"https://maxkle1nz.github.io/n3x1s-blog/about.html"
"https://maxkle1nz.github.io/n3x1s-blog/category-web-scraping.html"
"https://maxkle1nz.github.io/n3x1s-blog/category-data-engineering.html"
"https://maxkle1nz.github.io/n3x1s-blog/category-automation.html"
"https://maxkle1nz.github.io/n3x1s-blog/category-apis.html"
"https://maxkle1nz.github.io/n3x1s-blog/category-tutorials.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_building-a-job-scraper-indeed-linkedin-glassdoor.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_building-a-price-tracker-with-python-and-beautifulsoup.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_building-a-real-estate-price-tracker-with-python.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_data-enrichment-how-to-add-value-to-raw-scraped-data.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_data-pipeline-architecture-from-messy-csvs-to-clean-database.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_deploying-python-scrapers-on-linux-vps-complete-setup.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_fastapi-vs-flask-for-data-apis-which-to-choose-in-2026.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_how-to-avoid-getting-blocked-while-web-scraping.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_how-to-build-an-etl-pipeline-with-python-and-mysql.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_how-to-extract-data-from-pdfs-with-python.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_how-to-reverse-engineer-apis-for-data-extraction.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_how-to-schedule-python-scripts-to-run-automatically.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_how-to-scrape-javascript-heavy-websites-with-playwright.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_how-to-scrape-yelp-with-python-step-by-step-guide-2026.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_how-to-store-scraped-data-csv-vs-json-vs-database.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_python-automation-12-scripts-that-save-hours-every-week.html"
"https://maxkle1nz.github.io/n3x1s-blog/20260302_web-scraping-vs-api-when-to-use-each-with-examples.html"
)

# Build JSON array
URL_JSON=$(printf '"%s",' "${URLS[@]}" | sed 's/,$//')

# Submit to IndexNow endpoints
ENDPOINTS=(
"https://api.indexnow.org/indexnow"
"https://www.bing.com/indexnow"
"https://yandex.com/indexnow"
)

for ENDPOINT in "${ENDPOINTS[@]}"; do
    echo "Submitting to $ENDPOINT..."
    curl -s -X POST "$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{
            \"host\": \"$HOST\",
            \"key\": \"$KEY\",
            \"keyLocation\": \"$KEY_LOCATION\",
            \"urlList\": [$URL_JSON]
        }" && echo ""
done
