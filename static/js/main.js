let jsConfig = {
    'editFormUrl': '',
    'editFormActionUrl': ''
};

jsConfig.init = function() {
    jsConfig.editClickEvent();
};

// Edit transaction click event
jsConfig.editClickEvent = function() {
    document.querySelectorAll('.editable').forEach(function(e) {
        e.addEventListener('click', function(e) {
            let target = e.target;
            let targetId = target.dataset.id;
            let targetType = target.dataset.type;

            if (targetId === undefined) {
                target = target.closest('[data-id]');
                targetId = target.dataset.id;
                targetType = target.dataset.type;
            }

            if (!targetId) {
                return;
            }

            // Remove existing forms
            let clickingExistingForm = false;
            document.querySelectorAll(`.edit-form`).forEach(function(e) {
                clickingExistingForm =  targetId === e.dataset.id;
                e.remove()
            });

            let fullEndpoint = `${jsConfig.editFormUrl}/${targetId}/${targetType}`;
            if (targetId === 'add') {
                fullEndpoint = jsConfig.editFormUrl;
            }

            // Only show the form is user is not clicking on same form that's already open (UX shortcut)
            if (!clickingExistingForm) {
                fetchWrapper(fullEndpoint, 'get', {}, function(data) {
                    jsConfig.addEditForm(target, data);
                });
            }
        });
    });
};

jsConfig.addEditForm = function(transactionRow, data) {
    let top = `${transactionRow.offsetTop + transactionRow.offsetHeight}px`;
    let left = `${transactionRow.offsetLeft}px`;
    let wrapperDiv = document.createElement('div');
    wrapperDiv.style = `position: absolute; top: ${top}; left: ${left};`;
    wrapperDiv.innerHTML = data.html;

    // Add click events to control divs
    let controlDivs = wrapperDiv.querySelectorAll('.edit-form-action');
    controlDivs.forEach(function(e) {
        e.addEventListener('click', function(e) {
            jsConfig.editFormAction(e.target);
        });
    });

    document.body.appendChild(wrapperDiv);
};

jsConfig.editFormAction = function(controlDiv) {
    let action = controlDiv.dataset.action;
    switch (action) {
        case 'close':
            // TODO - need to remove .edit-form's PARENT node
            controlDiv.closest('.edit-form').remove();
            return;
            break;
        case 'add-group':
            // Unhide the add group form, hide transaction group inputs
            jsConfig.toggleAddGroupForm(controlDiv);
            return;
            break;
        case 'delete':
            if (!confirm(`Are you sure you\'d like to delete this ${controlDiv.dataset.type}?`)) {
                return;
            }
            break;
    }

    let params = {
        'action': action,
        'objectId': controlDiv.dataset.id,
        'objectType': controlDiv.dataset.type
    };
    fetchWrapper(jsConfig.editFormActionUrl, 'post', params, function() {
        location.reload();
    });
};

jsConfig.toggleAddGroupForm = function(controlDiv) {
    let showForm = !hasClass(controlDiv, 'active');
    let addFromWrapper = document.querySelector('.add-group-form-wrapper');
    let groupNameInput = document.querySelector('input[name="group_name"]');

    jsConfig.showHideTransactionTypeSelects(showForm);
    if (showForm) {
        removeClass(addFromWrapper, 'hidden');
        addClass(controlDiv, 'active');
        groupNameInput.required = true;
    }   else {
        addClass(addFromWrapper, 'hidden');
        removeClass(controlDiv, 'active');
        groupNameInput.required = false;
    }
};

jsConfig.showHideTransactionTypeSelects = function(show) {
    let transactionGroupSelect = document.querySelector('select[name="group"]');
    let transactionTypeSelect = document.querySelector('select[name="type"]');
    if (transactionGroupSelect) {
        if (show) {
            addClass(transactionGroupSelect.parentNode, 'hidden');
        } else {
            removeClass(transactionGroupSelect.parentNode, 'hidden');
        }
    }
    if (transactionTypeSelect) {
        if (show) {
            addClass(transactionTypeSelect.parentNode, 'hidden');
        } else {
            removeClass(transactionTypeSelect.parentNode, 'hidden');
        }
    }
};