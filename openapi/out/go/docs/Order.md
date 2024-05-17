# Order

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **int32** |  | [optional] 
**Priority** | Pointer to **string** | Priority (low, normal, high) | [optional] [default to "normal"]
**UserId** | **int32** |  | 
**Timestamp** | Pointer to **int64** | A Unix timestamp in milliseconds. The timestamp is used to determine the time of creation of an object. | [optional] 
**CarId** | **int32** |  | 
**Notification** | Pointer to **string** |  | [optional] 
**TargetStopId** | **int32** |  | 
**StopRouteId** | **int32** |  | 
**NotificationPhone** | Pointer to [**MobilePhone**](MobilePhone.md) |  | [optional] 
**LastState** | Pointer to [**OrderState**](OrderState.md) |  | [optional] 

## Methods

### NewOrder

`func NewOrder(userId int32, carId int32, targetStopId int32, stopRouteId int32, ) *Order`

NewOrder instantiates a new Order object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewOrderWithDefaults

`func NewOrderWithDefaults() *Order`

NewOrderWithDefaults instantiates a new Order object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *Order) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *Order) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *Order) SetId(v int32)`

SetId sets Id field to given value.

### HasId

`func (o *Order) HasId() bool`

HasId returns a boolean if a field has been set.

### GetPriority

`func (o *Order) GetPriority() string`

GetPriority returns the Priority field if non-nil, zero value otherwise.

### GetPriorityOk

`func (o *Order) GetPriorityOk() (*string, bool)`

GetPriorityOk returns a tuple with the Priority field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPriority

`func (o *Order) SetPriority(v string)`

SetPriority sets Priority field to given value.

### HasPriority

`func (o *Order) HasPriority() bool`

HasPriority returns a boolean if a field has been set.

### GetUserId

`func (o *Order) GetUserId() int32`

GetUserId returns the UserId field if non-nil, zero value otherwise.

### GetUserIdOk

`func (o *Order) GetUserIdOk() (*int32, bool)`

GetUserIdOk returns a tuple with the UserId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserId

`func (o *Order) SetUserId(v int32)`

SetUserId sets UserId field to given value.


### GetTimestamp

`func (o *Order) GetTimestamp() int64`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *Order) GetTimestampOk() (*int64, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *Order) SetTimestamp(v int64)`

SetTimestamp sets Timestamp field to given value.

### HasTimestamp

`func (o *Order) HasTimestamp() bool`

HasTimestamp returns a boolean if a field has been set.

### GetCarId

`func (o *Order) GetCarId() int32`

GetCarId returns the CarId field if non-nil, zero value otherwise.

### GetCarIdOk

`func (o *Order) GetCarIdOk() (*int32, bool)`

GetCarIdOk returns a tuple with the CarId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCarId

`func (o *Order) SetCarId(v int32)`

SetCarId sets CarId field to given value.


### GetNotification

`func (o *Order) GetNotification() string`

GetNotification returns the Notification field if non-nil, zero value otherwise.

### GetNotificationOk

`func (o *Order) GetNotificationOk() (*string, bool)`

GetNotificationOk returns a tuple with the Notification field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNotification

`func (o *Order) SetNotification(v string)`

SetNotification sets Notification field to given value.

### HasNotification

`func (o *Order) HasNotification() bool`

HasNotification returns a boolean if a field has been set.

### GetTargetStopId

`func (o *Order) GetTargetStopId() int32`

GetTargetStopId returns the TargetStopId field if non-nil, zero value otherwise.

### GetTargetStopIdOk

`func (o *Order) GetTargetStopIdOk() (*int32, bool)`

GetTargetStopIdOk returns a tuple with the TargetStopId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTargetStopId

`func (o *Order) SetTargetStopId(v int32)`

SetTargetStopId sets TargetStopId field to given value.


### GetStopRouteId

`func (o *Order) GetStopRouteId() int32`

GetStopRouteId returns the StopRouteId field if non-nil, zero value otherwise.

### GetStopRouteIdOk

`func (o *Order) GetStopRouteIdOk() (*int32, bool)`

GetStopRouteIdOk returns a tuple with the StopRouteId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStopRouteId

`func (o *Order) SetStopRouteId(v int32)`

SetStopRouteId sets StopRouteId field to given value.


### GetNotificationPhone

`func (o *Order) GetNotificationPhone() MobilePhone`

GetNotificationPhone returns the NotificationPhone field if non-nil, zero value otherwise.

### GetNotificationPhoneOk

`func (o *Order) GetNotificationPhoneOk() (*MobilePhone, bool)`

GetNotificationPhoneOk returns a tuple with the NotificationPhone field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNotificationPhone

`func (o *Order) SetNotificationPhone(v MobilePhone)`

SetNotificationPhone sets NotificationPhone field to given value.

### HasNotificationPhone

`func (o *Order) HasNotificationPhone() bool`

HasNotificationPhone returns a boolean if a field has been set.

### GetLastState

`func (o *Order) GetLastState() OrderState`

GetLastState returns the LastState field if non-nil, zero value otherwise.

### GetLastStateOk

`func (o *Order) GetLastStateOk() (*OrderState, bool)`

GetLastStateOk returns a tuple with the LastState field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLastState

`func (o *Order) SetLastState(v OrderState)`

SetLastState sets LastState field to given value.

### HasLastState

`func (o *Order) HasLastState() bool`

HasLastState returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


