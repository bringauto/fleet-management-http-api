# \StopAPI

All URIs are relative to */v2/management*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateStop**](StopAPI.md#CreateStop) | **Post** /stop | Create a new Stop.
[**DeleteStop**](StopAPI.md#DeleteStop) | **Delete** /stop/{stopId} | Delete a Stop with the specified ID.
[**GetStop**](StopAPI.md#GetStop) | **Get** /stop/{stopId} | Find and return a single Stop by its ID.
[**GetStops**](StopAPI.md#GetStops) | **Get** /stop | Find and return all existing Stops.
[**UpdateStop**](StopAPI.md#UpdateStop) | **Put** /stop | Update already existing Stop.



## CreateStop

> Stop CreateStop(ctx).Stop(stop).Execute()

Create a new Stop.

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
	stop := *openapiclient.NewStop("Lidická", *openapiclient.NewGNSSPosition()) // Stop | Stop model in JSON format.

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StopAPI.CreateStop(context.Background()).Stop(stop).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StopAPI.CreateStop``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateStop`: Stop
	fmt.Fprintf(os.Stdout, "Response from `StopAPI.CreateStop`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateStopRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stop** | [**Stop**](Stop.md) | Stop model in JSON format. | 

### Return type

[**Stop**](Stop.md)

### Authorization

[oAuth2AuthCode](../README.md#oAuth2AuthCode), [APIKeyAuth](../README.md#APIKeyAuth)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteStop

> DeleteStop(ctx, stopId).Execute()

Delete a Stop with the specified ID.

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
	stopId := int32(1) // int32 | ID of the Stop to be deleted.

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.StopAPI.DeleteStop(context.Background(), stopId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StopAPI.DeleteStop``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**stopId** | **int32** | ID of the Stop to be deleted. | 

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteStopRequest struct via the builder pattern


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


## GetStop

> Stop GetStop(ctx, stopId).Execute()

Find and return a single Stop by its ID.

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
	stopId := int32(1) // int32 | ID of Stop to be returned.

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.StopAPI.GetStop(context.Background(), stopId).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StopAPI.GetStop``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStop`: Stop
	fmt.Fprintf(os.Stdout, "Response from `StopAPI.GetStop`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**stopId** | **int32** | ID of Stop to be returned. | 

### Other Parameters

Other parameters are passed through a pointer to a apiGetStopRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


### Return type

[**Stop**](Stop.md)

### Authorization

[oAuth2AuthCode](../README.md#oAuth2AuthCode), [APIKeyAuth](../README.md#APIKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetStops

> []Stop GetStops(ctx).Execute()

Find and return all existing Stops.

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
	resp, r, err := apiClient.StopAPI.GetStops(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StopAPI.GetStops``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetStops`: []Stop
	fmt.Fprintf(os.Stdout, "Response from `StopAPI.GetStops`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetStopsRequest struct via the builder pattern


### Return type

[**[]Stop**](Stop.md)

### Authorization

[oAuth2AuthCode](../README.md#oAuth2AuthCode), [APIKeyAuth](../README.md#APIKeyAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateStop

> UpdateStop(ctx).Stop(stop).Execute()

Update already existing Stop.

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
	stop := *openapiclient.NewStop("Lidická", *openapiclient.NewGNSSPosition()) // Stop | JSON representation of the updated Stop.

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.StopAPI.UpdateStop(context.Background()).Stop(stop).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `StopAPI.UpdateStop``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUpdateStopRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stop** | [**Stop**](Stop.md) | JSON representation of the updated Stop. | 

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

