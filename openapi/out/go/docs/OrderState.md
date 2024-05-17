# OrderState

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **int32** |  | [optional] 
**Status** | [**OrderStatus**](OrderStatus.md) |  | 
**OrderId** | **int32** |  | 
**Timestamp** | Pointer to **int64** | A Unix timestamp in milliseconds. The timestamp is used to determine the time of creation of an object. | [optional] 

## Methods

### NewOrderState

`func NewOrderState(status OrderStatus, orderId int32, ) *OrderState`

NewOrderState instantiates a new OrderState object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewOrderStateWithDefaults

`func NewOrderStateWithDefaults() *OrderState`

NewOrderStateWithDefaults instantiates a new OrderState object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *OrderState) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *OrderState) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *OrderState) SetId(v int32)`

SetId sets Id field to given value.

### HasId

`func (o *OrderState) HasId() bool`

HasId returns a boolean if a field has been set.

### GetStatus

`func (o *OrderState) GetStatus() OrderStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *OrderState) GetStatusOk() (*OrderStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *OrderState) SetStatus(v OrderStatus)`

SetStatus sets Status field to given value.


### GetOrderId

`func (o *OrderState) GetOrderId() int32`

GetOrderId returns the OrderId field if non-nil, zero value otherwise.

### GetOrderIdOk

`func (o *OrderState) GetOrderIdOk() (*int32, bool)`

GetOrderIdOk returns a tuple with the OrderId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrderId

`func (o *OrderState) SetOrderId(v int32)`

SetOrderId sets OrderId field to given value.


### GetTimestamp

`func (o *OrderState) GetTimestamp() int64`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *OrderState) GetTimestampOk() (*int64, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *OrderState) SetTimestamp(v int64)`

SetTimestamp sets Timestamp field to given value.

### HasTimestamp

`func (o *OrderState) HasTimestamp() bool`

HasTimestamp returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


