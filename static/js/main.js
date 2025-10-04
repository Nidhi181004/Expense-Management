// Main JavaScript for Expense Management System

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add loading state to buttons on form submission (for non-AJAX forms)
    $('form:not([data-ajax])').on('submit', function() {
        const $submitBtn = $(this).find('button[type="submit"]');
        const originalText = $submitBtn.html();
        
        $submitBtn.prop('disabled', true).html(
            '<i class="fas fa-spinner fa-spin me-2"></i>Processing...'
        );
        
        // Store original text for potential reset
        $submitBtn.data('original-text', originalText);
    });

    // Add fade-in animation to cards
    $('.card').addClass('fade-in');

    // Format currency inputs
    $('input[type="number"][step="0.01"]').on('input', function() {
        const value = parseFloat($(this).val());
        if (!isNaN(value)) {
            $(this).val(value.toFixed(2));
        }
    });

    // Auto-resize textareas
    $('textarea').on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});

// Utility Functions
const ExpenseManager = {
    // Format currency with symbol
    formatCurrency: function(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // Format date
    formatDate: function(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    // Get status badge class
    getStatusBadgeClass: function(status) {
        const statusClasses = {
            'approved': 'bg-success',
            'rejected': 'bg-danger',
            'pending': 'bg-warning',
            'pending_approval': 'bg-warning',
            'paid': 'bg-info',
            'draft': 'bg-secondary',
            'submitted': 'bg-primary'
        };
        return statusClasses[status] || 'bg-secondary';
    },

    // Show loading spinner
    showLoading: function(element) {
        const originalHtml = element.html();
        element.data('original-html', originalHtml);
        element.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Loading...');
    },

    // Hide loading spinner
    hideLoading: function(element) {
        const originalHtml = element.data('original-html');
        element.prop('disabled', false).html(originalHtml);
    },

    // Reset button state (for form buttons)
    resetButton: function(element) {
        const originalText = element.data('original-text') || element.html();
        element.prop('disabled', false).html(originalText);
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // Create toast container if it doesn't exist
        if (!$('#toast-container').length) {
            $('body').append('<div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3"></div>');
        }
        
        const $toast = $(toastHtml);
        $('#toast-container').append($toast);
        
        const toast = new bootstrap.Toast($toast[0]);
        toast.show();
        
        // Remove toast element after it's hidden
        $toast.on('hidden.bs.toast', function() {
            $(this).remove();
        });
    },

    // Confirm dialog
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },

    // AJAX helper
    ajax: function(options) {
        const defaults = {
            type: 'GET',
            dataType: 'json',
            contentType: 'application/json',
            beforeSend: function() {
                if (options.loadingElement) {
                    ExpenseManager.showLoading(options.loadingElement);
                }
            },
            complete: function() {
                if (options.loadingElement) {
                    ExpenseManager.hideLoading(options.loadingElement);
                }
            },
            error: function(xhr, status, error) {
                let message = 'An error occurred';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    message = xhr.responseJSON.error;
                }
                ExpenseManager.showToast(message, 'danger');
            }
        };
        
        return $.ajax($.extend(defaults, options));
    }
};

// Expense-specific functions
const ExpenseActions = {
    // View expense details
    viewDetails: function(expenseId) {
        ExpenseManager.ajax({
            url: `/api/expenses/${expenseId}`,
            success: function(data) {
                ExpenseActions.showExpenseModal(data);
            }
        });
    },

    // Show expense details in modal
    showExpenseModal: function(expense) {
        const modalHtml = `
            <div class="modal fade" id="expenseDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-receipt me-2"></i>${expense.title}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="text-primary">Expense Information</h6>
                                    <table class="table table-sm">
                                        <tr><td><strong>Description:</strong></td><td>${expense.description || 'N/A'}</td></tr>
                                        <tr><td><strong>Amount:</strong></td><td>${expense.currency} ${expense.amount}</td></tr>
                                        <tr><td><strong>Date:</strong></td><td>${ExpenseManager.formatDate(expense.expense_date)}</td></tr>
                                        <tr><td><strong>Category:</strong></td><td>${expense.category}</td></tr>
                                        <tr><td><strong>Employee:</strong></td><td>${expense.employee}</td></tr>
                                        <tr><td><strong>Status:</strong></td><td>
                                            <span class="badge ${ExpenseManager.getStatusBadgeClass(expense.status)}">${expense.status}</span>
                                        </td></tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="text-primary">Approval Workflow</h6>
                                    ${expense.approvals.length > 0 ? 
                                        expense.approvals.map((approval, index) => `
                                            <div class="mb-2 p-2 border rounded">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <strong>Step ${index + 1}: ${approval.approver}</strong>
                                                    <span class="badge ${ExpenseManager.getStatusBadgeClass(approval.status)}">${approval.status}</span>
                                                </div>
                                                ${approval.comments ? `<small class="text-muted">${approval.comments}</small>` : ''}
                                                ${approval.approved_at ? `<br><small class="text-muted">Date: ${ExpenseManager.formatDate(approval.approved_at)}</small>` : ''}
                                            </div>
                                        `).join('') : 
                                        '<p class="text-muted">No approval workflow defined.</p>'
                                    }
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        $('#expenseDetailsModal').remove();
        
        // Add modal to body and show
        $('body').append(modalHtml);
        $('#expenseDetailsModal').modal('show');
        
        // Remove modal from DOM when hidden
        $('#expenseDetailsModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    },

    // Delete expense
    delete: function(expenseId, callback) {
        ExpenseManager.confirm('Are you sure you want to delete this expense?', function() {
            ExpenseManager.ajax({
                url: `/api/expenses/${expenseId}`,
                type: 'DELETE',
                success: function() {
                    ExpenseManager.showToast('Expense deleted successfully', 'success');
                    if (callback) callback();
                }
            });
        });
    }
};

// Approval-specific functions
const ApprovalActions = {
    // Approve expense
    approve: function(approvalId, comments, callback) {
        ExpenseManager.ajax({
            url: `/approvals/${approvalId}/approve`,
            type: 'POST',
            data: JSON.stringify({ comments: comments || '' }),
            success: function() {
                ExpenseManager.showToast('Expense approved successfully', 'success');
                if (callback) callback();
            }
        });
    },

    // Reject expense
    reject: function(approvalId, comments, callback) {
        if (!comments || !comments.trim()) {
            ExpenseManager.showToast('Please provide a reason for rejection', 'warning');
            return;
        }
        
        ExpenseManager.confirm('Are you sure you want to reject this expense?', function() {
            ExpenseManager.ajax({
                url: `/approvals/${approvalId}/reject`,
                type: 'POST',
                data: JSON.stringify({ comments: comments }),
                success: function() {
                    ExpenseManager.showToast('Expense rejected successfully', 'success');
                    if (callback) callback();
                }
            });
        });
    },

    // Bulk approve
    bulkApprove: function(approvalIds, callback) {
        ExpenseManager.confirm(`Are you sure you want to approve ${approvalIds.length} expenses?`, function() {
            // Implementation for bulk approve
            ExpenseManager.showToast('Bulk approve functionality would be implemented here', 'info');
        });
    },

    // Bulk reject
    bulkReject: function(approvalIds, callback) {
        const comments = prompt('Please provide a reason for bulk rejection:');
        if (!comments) return;
        
        ExpenseManager.confirm(`Are you sure you want to reject ${approvalIds.length} expenses?`, function() {
            // Implementation for bulk reject
            ExpenseManager.showToast('Bulk reject functionality would be implemented here', 'info');
        });
    }
};

// Currency conversion functions
const CurrencyManager = {
    // Get exchange rate
    getExchangeRate: function(fromCurrency, toCurrency, callback) {
        if (fromCurrency === toCurrency) {
            callback(1.0);
            return;
        }
        
        ExpenseManager.ajax({
            url: `/api/exchange-rate/${fromCurrency}/${toCurrency}`,
            success: function(data) {
                callback(data.rate);
            },
            error: function() {
                callback(1.0); // Fallback rate
            }
        });
    },

    // Convert amount
    convertAmount: function(amount, fromCurrency, toCurrency, callback) {
        this.getExchangeRate(fromCurrency, toCurrency, function(rate) {
            const convertedAmount = amount * rate;
            callback(convertedAmount, rate);
        });
    },

    // Update conversion display
    updateConversionDisplay: function(amount, fromCurrency, toCurrency, displayElement) {
        if (!amount || fromCurrency === toCurrency) {
            displayElement.hide();
            return;
        }
        
        this.convertAmount(amount, fromCurrency, toCurrency, function(convertedAmount, rate) {
            displayElement.show().html(`
                <i class="fas fa-exchange-alt me-2"></i>
                ${fromCurrency} ${amount.toFixed(2)} = ${toCurrency} ${convertedAmount.toFixed(2)} 
                (Rate: ${rate.toFixed(4)})
            `);
        });
    }
};

// OCR functionality (mock implementation)
const OCRManager = {
    // Process receipt image
    processReceipt: function(file, callback) {
        if (!file) {
            ExpenseManager.showToast('Please select a receipt image first', 'warning');
            return;
        }
        
        // Mock OCR processing
        ExpenseManager.showToast('Processing receipt...', 'info');
        
        setTimeout(function() {
            // Mock extracted data
            const extractedData = {
                title: 'Restaurant Meal',
                description: 'Business lunch with client',
                amount: 45.50,
                date: new Date().toISOString().split('T')[0],
                merchant: 'The Gourmet Restaurant'
            };
            
            ExpenseManager.showToast('Receipt processed successfully!', 'success');
            callback(extractedData);
        }, 2000);
    },

    // Fill form with extracted data
    fillExpenseForm: function(data) {
        $('#title').val(data.title);
        $('#description').val(data.description);
        $('#amount').val(data.amount);
        $('#expense_date').val(data.date);
        
        // Trigger change events to update any dependent fields
        $('#amount, #currency').trigger('change');
    }
};

// User management functions
const UserManager = {
    // Toggle user status
    toggleStatus: function(userId, currentStatus, callback) {
        const action = currentStatus ? 'deactivate' : 'activate';
        ExpenseManager.confirm(`Are you sure you want to ${action} this user?`, function() {
            ExpenseManager.ajax({
                url: `/api/users/${userId}/toggle-status`,
                type: 'POST',
                success: function() {
                    ExpenseManager.showToast(`User ${action}d successfully`, 'success');
                    if (callback) callback();
                }
            });
        });
    },

    // Delete user
    delete: function(userId, callback) {
        ExpenseManager.confirm('Are you sure you want to delete this user? This action cannot be undone.', function() {
            ExpenseManager.ajax({
                url: `/api/users/${userId}`,
                type: 'DELETE',
                success: function() {
                    ExpenseManager.showToast('User deleted successfully', 'success');
                    if (callback) callback();
                }
            });
        });
    }
};

// Search and filter functions
const FilterManager = {
    // Initialize filters
    init: function() {
        // Debounced search
        let searchTimeout;
        $('#searchText').on('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                FilterManager.applyFilters();
            }, 500);
        });
        
        // Filter change handlers
        $('#statusFilter, #dateFrom, #dateTo').on('change', function() {
            FilterManager.applyFilters();
        });
    },

    // Apply filters (client-side for demo, should be server-side in production)
    applyFilters: function() {
        const searchText = $('#searchText').val().toLowerCase();
        const statusFilter = $('#statusFilter').val();
        const dateFrom = $('#dateFrom').val();
        const dateTo = $('#dateTo').val();
        
        $('tbody tr').each(function() {
            const $row = $(this);
            let show = true;
            
            // Text search
            if (searchText && !$row.text().toLowerCase().includes(searchText)) {
                show = false;
            }
            
            // Status filter
            if (statusFilter && !$row.find('.badge').text().toLowerCase().includes(statusFilter)) {
                show = false;
            }
            
            // Date filters would require more complex logic
            
            $row.toggle(show);
        });
    }
};

// Initialize filters when document is ready
$(document).ready(function() {
    FilterManager.init();
});

// Export functions for global access
window.ExpenseManager = ExpenseManager;
window.ExpenseActions = ExpenseActions;
window.ApprovalActions = ApprovalActions;
window.CurrencyManager = CurrencyManager;
window.OCRManager = OCRManager;
window.UserManager = UserManager;
window.FilterManager = FilterManager;
