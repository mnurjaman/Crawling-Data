$(document).ready(function () {
    const form = $('#crawlForm');
    const submitBtn = $('#submitBtn');
    const submitSpinner = submitBtn.find('.spinner-border');
    const loadingSpinner = $('#loadingSpinner');
    const resultsSection = $('#resultsSection');
    const errorAlert = $('#errorAlert');
    const successAlert = $('#successAlert');

    function showAlert(message, type) {
        const alert = type === 'error' ? errorAlert : successAlert;
        alert.html(message).show();
        setTimeout(() => alert.fadeOut(), 5000);
    }

    function setLoadingState(isLoading) {
        submitBtn.prop('disabled', isLoading);
        submitSpinner.toggleClass('d-none', !isLoading);
        loadingSpinner.css('display', isLoading ? 'flex' : 'none');
    }

    function displaySummary(summary) {
        const summaryContent = $('#summaryContent');
        summaryContent.html(`
            <div class="row">
                <div class="col-md-4 summary-item">
                    <strong>Total Links:</strong> ${summary.total_links}
                </div>
                <div class="col-md-4 summary-item">
                    <strong>Internal Links:</strong> ${summary.internal_links}
                </div>
                <div class="col-md-4 summary-item">
                    <strong>External Links:</strong> ${summary.external_links}
                </div>
                <div class="col-md-4 summary-item">
                    <strong>Media Links:</strong> ${summary.media_links}
                </div>
                <div class="col-md-4 summary-item">
                    <strong>Pages Crawled:</strong> ${summary.pages_crawled}
                </div>
                <div class="col-md-4 summary-item">
                    <strong>Time Taken:</strong> ${summary.time_taken}
                </div>
            </div>
        `);
    }

    form.on('submit', function (event) {
        event.preventDefault();

        // Reset UI
        $('#linksTable tbody').empty();
        resultsSection.hide();
        errorAlert.hide();
        successAlert.hide();
        setLoadingState(true);

        $.ajax({
            url: '/',
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                if (response.status === "success") {
                    const tbody = $('#linksTable tbody');
                    response.links.forEach((link, index) => {
                        tbody.append(`
                            <tr>
                                <td class="text-center">${index + 1}</td>
                                <td><a href="${link.url}" target="_blank" rel="noopener noreferrer">${link.url}</a></td>
                                <td>${link.text}</td>
                                <td>${link.title}</td>
                                <td>${link.type}</td>
                            </tr>
                        `);
                    });

                    displaySummary(response.summary);

                    // Update download link
                    const filename = response.excel_file.split('/').pop();
                    $('#downloadBtn').attr('href', `/download/${filename}`);

                    resultsSection.show();
                    showAlert('Crawling selesai!', 'success');
                } else {
                    showAlert(response.message || 'Terjadi kesalahan saat crawling', 'error');
                }
            },
            error: function (xhr, status, error) {
                showAlert(`Terjadi kesalahan: ${error}`, 'error');
            },
            complete: function () {
                setLoadingState(false);
            }
        });
    });
});
