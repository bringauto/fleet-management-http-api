# CarState

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **int32** |  | [optional] 
**Timestamp** | Pointer to **int64** | A Unix timestamp in milliseconds. The timestamp is used to determine the time of creation of an object. | [optional] 
**Status** | [**CarStatus**](CarStatus.md) |  | 
**Fuel** | Pointer to **int32** |  | [optional] [default to 0]
**CarId** | **int32** |  | 
**Speed** | Pointer to **float32** |  | [optional] [default to 0.0]
**Position** | Pointer to [**GNSSPosition**](GNSSPosition.md) |  | [optional] 

## Methods

### NewCarState

`func NewCarState(status CarStatus, carId int32, ) *CarState`

NewCarState instantiates a new CarState object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCarStateWithDefaults

`func NewCarStateWithDefaults() *CarState`

NewCarStateWithDefaults instantiates a new CarState object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *CarState) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *CarState) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *CarState) SetId(v int32)`

SetId sets Id field to given value.

### HasId

`func (o *CarState) HasId() bool`

HasId returns a boolean if a field has been set.

### GetTimestamp

`func (o *CarState) GetTimestamp() int64`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *CarState) GetTimestampOk() (*int64, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *CarState) SetTimestamp(v int64)`

SetTimestamp sets Timestamp field to given value.

### HasTimestamp

`func (o *CarState) HasTimestamp() bool`

HasTimestamp returns a boolean if a field has been set.

### GetStatus

`func (o *CarState) GetStatus() CarStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *CarState) GetStatusOk() (*CarStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *CarState) SetStatus(v CarStatus)`

SetStatus sets Status field to given value.


### GetFuel

`func (o *CarState) GetFuel() int32`

GetFuel returns the Fuel field if non-nil, zero value otherwise.

### GetFuelOk

`func (o *CarState) GetFuelOk() (*int32, bool)`

GetFuelOk returns a tuple with the Fuel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFuel

`func (o *CarState) SetFuel(v int32)`

SetFuel sets Fuel field to given value.

### HasFuel

`func (o *CarState) HasFuel() bool`

HasFuel returns a boolean if a field has been set.

### GetCarId

`func (o *CarState) GetCarId() int32`

GetCarId returns the CarId field if non-nil, zero value otherwise.

### GetCarIdOk

`func (o *CarState) GetCarIdOk() (*int32, bool)`

GetCarIdOk returns a tuple with the CarId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCarId

`func (o *CarState) SetCarId(v int32)`

SetCarId sets CarId field to given value.


### GetSpeed

`func (o *CarState) GetSpeed() float32`

GetSpeed returns the Speed field if non-nil, zero value otherwise.

### GetSpeedOk

`func (o *CarState) GetSpeedOk() (*float32, bool)`

GetSpeedOk returns a tuple with the Speed field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSpeed

`func (o *CarState) SetSpeed(v float32)`

SetSpeed sets Speed field to given value.

### HasSpeed

`func (o *CarState) HasSpeed() bool`

HasSpeed returns a boolean if a field has been set.

### GetPosition

`func (o *CarState) GetPosition() GNSSPosition`

GetPosition returns the Position field if non-nil, zero value otherwise.

### GetPositionOk

`func (o *CarState) GetPositionOk() (*GNSSPosition, bool)`

GetPositionOk returns a tuple with the Position field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPosition

`func (o *CarState) SetPosition(v GNSSPosition)`

SetPosition sets Position field to given value.

### HasPosition

`func (o *CarState) HasPosition() bool`

HasPosition returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


