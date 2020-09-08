addEventListener('fetch', 
    event => event.respondWith(handleRequest(event.request)),
    false);

async function handleRequest(request) {
    const forwardHeaders = new Headers(request.headers);
    forwardHeaders.append('Authorization', '<<AuthorizationHeader>>');

    const forwardURL = new URL(request.url);
    forwardURL.protocol = 'https://';
    forwardURL.host = '<<B2Hostname>>';

    if (forwardURL.pathname === '/') {
        return notFoundResponse();
    } else {
        forwardURL.pathname = `/file/<<B2BucketName>>${forwardURL.pathname}`;
    }

    const forwardRequest = new Request(forwardURL, {
        method: request.method,
        headers: forwardHeaders
    });

    const response = await fetch(forwardRequest);
    if (response.ok) {
        const returnResponse = new Response(response.body, response);
        //<<ResponseAdditions>>
        return returnResponse;
    }

    return notFoundResponse();
}

function notFoundResponse() {
    return new Response('', { 'status' : 404, 'statusText': 'Not Found' });
}