# Car

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **int32** |  | [optional] 
**PlatformHwId** | **int32** |  | 
**Name** | **string** |  | 
**CarAdminPhone** | [**MobilePhone**](MobilePhone.md) |  | 
**DefaultRouteId** | Pointer to **int32** |  | [optional] 
**UnderTest** | Pointer to **bool** |  | [optional] [default to true]
**LastState** | Pointer to [**CarState**](CarState.md) |  | [optional] 

## Methods

### NewCar

`func NewCar(platformHwId int32, name string, carAdminPhone MobilePhone, ) *Car`

NewCar instantiates a new Car object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCarWithDefaults

`func NewCarWithDefaults() *Car`

NewCarWithDefaults instantiates a new Car object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *Car) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *Car) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *Car) SetId(v int32)`

SetId sets Id field to given value.

### HasId

`func (o *Car) HasId() bool`

HasId returns a boolean if a field has been set.

### GetPlatformHwId

`func (o *Car) GetPlatformHwId() int32`

GetPlatformHwId returns the PlatformHwId field if non-nil, zero value otherwise.

### GetPlatformHwIdOk

`func (o *Car) GetPlatformHwIdOk() (*int32, bool)`

GetPlatformHwIdOk returns a tuple with the PlatformHwId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPlatformHwId

`func (o *Car) SetPlatformHwId(v int32)`

SetPlatformHwId sets PlatformHwId field to given value.


### GetName

`func (o *Car) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *Car) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *Car) SetName(v string)`

SetName sets Name field to given value.


### GetCarAdminPhone

`func (o *Car) GetCarAdminPhone() MobilePhone`

GetCarAdminPhone returns the CarAdminPhone field if non-nil, zero value otherwise.

### GetCarAdminPhoneOk

`func (o *Car) GetCarAdminPhoneOk() (*MobilePhone, bool)`

GetCarAdminPhoneOk returns a tuple with the CarAdminPhone field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCarAdminPhone

`func (o *Car) SetCarAdminPhone(v MobilePhone)`

SetCarAdminPhone sets CarAdminPhone field to given value.


### GetDefaultRouteId

`func (o *Car) GetDefaultRouteId() int32`

GetDefaultRouteId returns the DefaultRouteId field if non-nil, zero value otherwise.

### GetDefaultRouteIdOk

`func (o *Car) GetDefaultRouteIdOk() (*int32, bool)`

GetDefaultRouteIdOk returns a tuple with the DefaultRouteId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDefaultRouteId

`func (o *Car) SetDefaultRouteId(v int32)`

SetDefaultRouteId sets DefaultRouteId field to given value.

### HasDefaultRouteId

`func (o *Car) HasDefaultRouteId() bool`

HasDefaultRouteId returns a boolean if a field has been set.

### GetUnderTest

`func (o *Car) GetUnderTest() bool`

GetUnderTest returns the UnderTest field if non-nil, zero value otherwise.

### GetUnderTestOk

`func (o *Car) GetUnderTestOk() (*bool, bool)`

GetUnderTestOk returns a tuple with the UnderTest field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUnderTest

`func (o *Car) SetUnderTest(v bool)`

SetUnderTest sets UnderTest field to given value.

### HasUnderTest

`func (o *Car) HasUnderTest() bool`

HasUnderTest returns a boolean if a field has been set.

### GetLastState

`func (o *Car) GetLastState() CarState`

GetLastState returns the LastState field if non-nil, zero value otherwise.

### GetLastStateOk

`func (o *Car) GetLastStateOk() (*CarState, bool)`

GetLastStateOk returns a tuple with the LastState field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLastState

`func (o *Car) SetLastState(v CarState)`

SetLastState sets LastState field to given value.

### HasLastState

`func (o *Car) HasLastState() bool`

HasLastState returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


