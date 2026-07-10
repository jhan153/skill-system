public sealed class CheckoutController
{
    public Response CreateOrder(Request request)
    {
        try
        {
            var order = Order.From(request);
            repository.Save(order);
            return Response.Json(201, new { status = "created" });
        }
        catch (ArgumentException)
        {
            return Response.Json(500, new { error = "INTERNAL_ERROR" });
        }
    }

    public Response CancelOrder(string id)
    {
        var order = repository.Get(id);
        repository.Delete(order);
        return Response.Json(204, null);
    }
}
