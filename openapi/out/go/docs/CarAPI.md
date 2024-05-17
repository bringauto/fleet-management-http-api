# \CarAPI

All URIs are relative to */v2/management*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateCar**](CarAPI.md#CreateCar) | **Post** /car | Create a new Car object.
[**DeleteCar**](CarAPI.md#DeleteCar) | **Delete** /car/{carId} | Delete a Car identified by its ID.
[**GetCar**](CarAPI.md#GetCar) | **Get** /car/{carId} | Find a single Car by its ID.
[**GetCars**](CarAPI.md#GetCars) | **Get** /car | Find and return all existing Cars.
[**UpdateCar**](CarAPI.md#UpdateCar) | **Put** /car | Update already existing Car.



## CreateCar

> Car CreateCar(ctx).Car(car).Execute()

Create a new Car object.

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	car := *openapiclient.NewCar(int32(1), "BAT-2022-01", *openapiclient.NewMobilePhone()) // Car | A Car model in JSON format.

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CarAPI.CreateCar(context.Background()).Car(car).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CarAPI.CreateCar``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateCar`: Car
	fmt.Fprintf(os.Stdout, "Response from `CarAPI.CreateCar`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateCarRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **car** | [**Car**](Car.md) | A Car model in JSON format. | 

### Return type

[**Car**](Car.md)

### Authorization

[oAuth2AuthCode](../README.md#oAuth2AuthCode), [APIKeyAuth](../README.md#APIKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteCar

> DeleteCar(ctx, carId).Execute()

Delete a Car identified by its ID.

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	carId := int32(1) // int32 | The ID of the Car to be deleted.

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.CarAPI.DeleteCar(context.Background(), carId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CarAPI.DeleteCar``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**carId** | **int32** | The ID of the Car to be deleted. | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteCarRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

 (empty response body)

### Authorization

[oAuth2AuthCode](../README.md#oAuth2AuthCode), [APIKeyAuth](../README.md#APIKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: text/plain, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetCar

> Car GetCar(ctx, carId).Execute()

Find a single Car by its ID.

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	carId := int32(1) // int32 | An ID of the Car to be returned.

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CarAPI.GetCar(context.Background(), carId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CarAPI.GetCar``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetCar`: Car
	fmt.Fprintf(os.Stdout, "Response from `CarAPI.GetCar`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**carId** | **int32** | An ID of the Car to be returned. | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetCarRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**Car**](Car.md)

### Authorization

[oAuth2AuthCode](../README.md#oAuth2AuthCode), [APIKeyAuth](../README.md#APIKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetCars

> []Car GetCars(ctx).Execute()

Find and return all existing Cars.

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CarAPI.GetCars(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CarAPI.GetCars``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetCars`: []Car
	fmt.Fprintf(os.Stdout, "Response from `CarAPI.GetCars`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetCarsRequest struct via the builder pattern


### Return type

[**[]Car**](Car.md)

### Authorization

[oAuth2AuthCode](../README.md#oAuth2AuthCode), [APIKeyAuth](../README.md#APIKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateCar

> UpdateCar(ctx).Car(car).Execute()

Update already existing Car.

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/GIT_USER_ID/GIT_REPO_ID"
)

func main() {
	car := *openapiclient.NewCar(int32(1), "BAT-2022-01", *openapiclient.NewMobilePhone()) // Car | JSON representation of the updated Car.

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.CarAPI.UpdateCar(context.Background()).Car(car).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CarAPI.UpdateCar``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUpdateCarRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **car** | [**Car**](Car.md) | JSON representation of the updated Car. | 

### Return type

 (empty response body)

### Authorization

[oAuth2AuthCode](../README.md#oAuth2AuthCode), [APIKeyAuth](../README.md#APIKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: text/plain, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)

