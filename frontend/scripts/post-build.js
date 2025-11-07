import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const builtHtmlPath = path.join(__dirname, '../../forms_pro/public/frontend/index.html');
const targetHtmlPath = path.join(__dirname, '../../forms_pro/www/frontend.html');

// Read the built HTML file
let htmlContent = fs.readFileSync(builtHtmlPath, 'utf8');

// Replace the old boot data injection with the corrected version
// that properly handles datetime objects and other non-JSON-serializable types
const oldBootScriptPattern = /<script>[\s\S]*?{% for key in boot %}[\s\S]*?{% endfor %}[\s\S]*?<\/script>/;
const newBootScript = `<script>
              (function() {
                  const bootData = {{ boot | safe }};
                  for (const key in bootData) {
                      window[key] = bootData[key];
                  }
                  window.csrf_token = "{{ csrf_token }}";
              })();
          </script>`;

if (oldBootScriptPattern.test(htmlContent)) {
    htmlContent = htmlContent.replace(oldBootScriptPattern, newBootScript);
} else {
    // If the pattern doesn't match, try to find any script tag before </body> and replace it
    const scriptBeforeBodyPattern = /(<script>[\s\S]*?<\/script>)(\s*<\/body>)/;
    if (scriptBeforeBodyPattern.test(htmlContent)) {
        htmlContent = htmlContent.replace(scriptBeforeBodyPattern, `${newBootScript}$2`);
    } else {
        // If no script found, insert before </body>
        htmlContent = htmlContent.replace('</body>', `${newBootScript}\n          </body>`);
    }
}

// Write the processed HTML to www directory
fs.writeFileSync(targetHtmlPath, htmlContent);

console.log('✅ HTML template processed and copied to www/frontend.html');
console.log('✅ Jinja boot data and CSRF token injection added');

