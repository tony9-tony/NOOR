from pathlib import Path
import re

root = Path(r'c:\Users\user\Desktop\NOOR\.vscode')

parts_markup = '''        <div class="parts-slider">
            <h3>Parts Carousel</h3>
            <div class="parts-display" id="part-display">
                <div class="part-card">
                    <div class="part-image-placeholder" id="part-image-placeholder">Chagua sehemu kwa kutumia mishale</div>
                    <div class="part-info">
                        <h4 id="part-name">Sehemu ya gari</h4>
                        <p id="part-description">Maelezo ya sehemu yanaonekana hapa.</p>
                    </div>
                </div>
            </div>
            <div class="parts-controls">
                <a href="#" id="prev-part" class="car-nav-btn" aria-label="Previous part">&#10094;</a>
                <a href="#" id="next-part" class="car-nav-btn" aria-label="Next part">&#10095;</a>
            </div>
        </div>
'''

car_parts_block = '''const carParts = [
            { name: 'Engine Air Filter', description: 'Inapunguza uchafu kwenye hewa ya injini ili kuboresha utendaji na maisha ya injini.' },
            { name: 'Brake Pads', description: 'Karatasi za breki za ubora wa juu kwa kusimama salama na thabiti.' },
            { name: 'Headlight Assembly', description: 'Mwangaza wa mbele wa LED/halogen kwa usafi bora wa mwanga usiku.' },
            { name: 'Alloy Wheel', description: 'Magurudumu ya chuma yaliyofanywa kwa uzuri na uimara wa barabara.' },
            { name: 'Infotainment System', description: 'Skrini ya kugusa na mfumo wa sauti kwa urahisi wa kuzungumza na kusafiri.' }
        ];'''

for path in sorted(root.glob('*.html')):
    text = path.read_text(encoding='utf-8')
    if 'id="car-image-display"' not in text or 'const carImages = [' not in text:
        continue
    if 'id="part-display"' in text or 'parts-slider' in text:
        continue
    if '</main>' not in text:
        continue

    text = text.replace('</main>', parts_markup + '    </main>', 1)
    match = re.search(r'<script>.*?</script>', text, re.S)
    if not match:
        continue
    old_script = match.group(0)
    car_images_match = re.search(r'const carImages = \[.*?\];', old_script, re.S)
    if not car_images_match:
        continue
    car_images_block = car_images_match.group(0)
    new_script = f'''    <script>
        {car_images_block}

        {car_parts_block}

        let currentImageIndex = 0;
        let currentPartIndex = 0;
        const imageElement = document.getElementById('car-image-display');
        const prevButton = document.getElementById('prev-car');
        const nextButton = document.getElementById('next-car');
        const partName = document.getElementById('part-name');
        const partDescription = document.getElementById('part-description');
        const partImagePlaceholder = document.getElementById('part-image-placeholder');
        const prevPart = document.getElementById('prev-part');
        const nextPart = document.getElementById('next-part');

        function showImage(index) {
            currentImageIndex = (index + carImages.length) % carImages.length;
            imageElement.src = carImages[currentImageIndex].src;
            imageElement.alt = carImages[currentImageIndex].alt;
        }

        function showPart(index) {
            currentPartIndex = (index + carParts.length) % carParts.length;
            const part = carParts[currentPartIndex];
            partName.textContent = part.name;
            partDescription.textContent = part.description;
            partImagePlaceholder.textContent = part.name;
        }

        prevButton.addEventListener('click', function (event) {
            event.preventDefault();
            showImage(currentImageIndex - 1);
        });

        nextButton.addEventListener('click', function (event) {
            event.preventDefault();
            showImage(currentImageIndex + 1);
        });

        prevPart.addEventListener('click', function (event) {
            event.preventDefault();
            showPart(currentPartIndex - 1);
        });

        nextPart.addEventListener('click', function (event) {
            event.preventDefault();
            showPart(currentPartIndex + 1);
        });

        showImage(currentImageIndex);
        showPart(currentPartIndex);
    </script>'''
    text = text[:match.start()] + new_script + text[match.end():]
    path.write_text(text, encoding='utf-8')
    print(f'Updated {path.name}')
