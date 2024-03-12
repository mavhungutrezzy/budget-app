function hasClass(el, className) {
    if (el.classList) {
        return el.classList.contains(className);
    }
    return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'));
}

function addClass(el, className) {
    if (el.classList) {
        el.classList.add(className);
    } else if (!hasClass(el, className)) {
        el.className += " " + className;
    }
}

function removeClass(el, className) {
    if (el.classList) {
        el.classList.remove(className);
    } else if (hasClass(el, className)) {
        var reg = new RegExp('(\\s|^)' + className + '(\\s|$)');
        el.className = el.className.replace(reg, ' ');
    }
}

function fetchWrapper(endpoint, method, params, callback) {
    var callParams = {
        method      : method,
        credentials : 'include'
    };
    if (params instanceof FormData) {
        callParams['body'] = params
    } else {
        if (method.toLowerCase() === 'post') {
            callParams['body'] = JSON.stringify(params);
        }
    }

    fetch(endpoint, callParams)
    .then((response) => {
        return response.text();
    })
    .then((data) => {
        let response = JSON.parse(data);
        if (!response.success ) {
            alert(response.message);
        } else {
            callback(response);
        }
    })
    .catch(function(ex) {
        console.log(ex);
    });
}
