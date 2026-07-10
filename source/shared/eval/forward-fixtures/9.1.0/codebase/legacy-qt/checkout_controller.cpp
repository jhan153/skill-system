#include <string>

Response CheckoutController::createOrder(const Request& request) {
    if (request.amountCents <= 0) {
        return Response{400, "{\"error\":\"INVALID_AMOUNT\"}"};
    }
    repository.save(Order::from(request));
    return Response{201, "{\"status\":\"created\"}"};
}

Response CheckoutController::cancelOrder(const std::string& id) {
    auto order = repository.get(id);
    order.cancel();
    repository.save(order);
    return Response{200, "{\"status\":\"cancelled\"}"};
}
