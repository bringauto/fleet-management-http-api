# Stop

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **int32** |  | [optional] 
**Name** | **string** |  | 
**Position** | [**GNSSPosition**](GNSSPosition.md) |  | 
**NotificationPhone** | Pointer to [**MobilePhone**](MobilePhone.md) |  | [optional] 

## Methods

### NewStop

`func NewStop(name string, position GNSSPosition, ) *Stop`

NewStop instantiates a new Stop object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStopWithDefaults

`func NewStopWithDefaults() *Stop`

NewStopWithDefaults instantiates a new Stop object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *Stop) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *Stop) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *Stop) SetId(v int32)`

SetId sets Id field to given value.

### HasId

`func (o *Stop) HasId() bool`

HasId returns a boolean if a field has been set.

### GetName

`func (o *Stop) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *Stop) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *Stop) SetName(v string)`

SetName sets Name field to given value.


### GetPosition

`func (o *Stop) GetPosition() GNSSPosition`

GetPosition returns the Position field if non-nil, zero value otherwise.

### GetPositionOk

`func (o *Stop) GetPositionOk() (*GNSSPosition, bool)`

GetPositionOk returns a tuple with the Position field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPosition

`func (o *Stop) SetPosition(v GNSSPosition)`

SetPosition sets Position field to given value.


### GetNotificationPhone

`func (o *Stop) GetNotificationPhone() MobilePhone`

GetNotificationPhone returns the NotificationPhone field if non-nil, zero value otherwise.

### GetNotificationPhoneOk

`func (o *Stop) GetNotificationPhoneOk() (*MobilePhone, bool)`

GetNotificationPhoneOk returns a tuple with the NotificationPhone field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNotificationPhone

`func (o *Stop) SetNotificationPhone(v MobilePhone)`

SetNotificationPhone sets NotificationPhone field to given value.

### HasNotificationPhone

`func (o *Stop) HasNotificationPhone() bool`

HasNotificationPhone returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


