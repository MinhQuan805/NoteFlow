# Download all CS224N lecture slides from Stanford
# Usage: .\download_cs224n_slides.ps1

# Create output directory
$outputDir = "cs224n_slides"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
    Write-Host "Created directory: $outputDir" -ForegroundColor Green
}

# List of all PDF URLs
$urls = @(
    "https://web.stanford.edu/class/cs224n/slides/cs224n-2024-lecture17-human-centered-nlp.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-2024-lecture18-deployment-and-efficiency.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-2024-lecture19-open-problems.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture01-wordvecs1.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture02-wordvecs2.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture03-neuralnets.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture04-dep-parsing.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture05-rnnlm.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture06-fancy-rnn.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture07-final-project.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture08-transformers.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture09-pretraining-updated.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture10-prompting-rlhf.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture11-evaluation-yann.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture12-training-shikhar.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture13-speech-bci.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture14-agents-shikhar-updated.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture15-life-after-dpo-lambert.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture16-CNN-TreeRNN.pdf",
    "https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture18-nlp-linguistics-philosophy.pdf"
)

Write-Host "`nDownloading $($urls.Count) PDF files..." -ForegroundColor Cyan
Write-Host "Output directory: $outputDir`n" -ForegroundColor Cyan

$downloaded = 0
$failed = 0

foreach ($url in $urls) {
    $filename = Split-Path $url -Leaf
    $outputPath = Join-Path $outputDir $filename
    
    try {
        Write-Host "[$($downloaded + $failed + 1)/$($urls.Count)] Downloading: $filename" -NoNewline
        Invoke-WebRequest -Uri $url -OutFile $outputPath -ErrorAction Stop
        Write-Host " ✓" -ForegroundColor Green
        $downloaded++
    }
    catch {
        Write-Host " ✗ FAILED" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Download complete!" -ForegroundColor Green
Write-Host "  Success: $downloaded files" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "  Failed:  $failed files" -ForegroundColor Red
}
Write-Host "  Location: $(Resolve-Path $outputDir)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
