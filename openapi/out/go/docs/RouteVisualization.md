# RouteVisualization

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | Pointer to **int32** |  | [optional] 
**RouteId** | **int32** |  | 
**Hexcolor** | Pointer to **string** | Color in hexadecimal format. | [optional] [default to "#FF0000"]
**Points** | [**[]GNSSPosition**](GNSSPosition.md) |  | [default to []]

## Methods

### NewRouteVisualization

`func NewRouteVisualization(routeId int32, points []GNSSPosition, ) *RouteVisualization`

NewRouteVisualization instantiates a new RouteVisualization object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewRouteVisualizationWithDefaults

`func NewRouteVisualizationWithDefaults() *RouteVisualization`

NewRouteVisualizationWithDefaults instantiates a new RouteVisualization object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *RouteVisualization) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *RouteVisualization) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *RouteVisualization) SetId(v int32)`

SetId sets Id field to given value.

### HasId

`func (o *RouteVisualization) HasId() bool`

HasId returns a boolean if a field has been set.

### GetRouteId

`func (o *RouteVisualization) GetRouteId() int32`

GetRouteId returns the RouteId field if non-nil, zero value otherwise.

### GetRouteIdOk

`func (o *RouteVisualization) GetRouteIdOk() (*int32, bool)`

GetRouteIdOk returns a tuple with the RouteId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRouteId

`func (o *RouteVisualization) SetRouteId(v int32)`

SetRouteId sets RouteId field to given value.


### GetHexcolor

`func (o *RouteVisualization) GetHexcolor() string`

GetHexcolor returns the Hexcolor field if non-nil, zero value otherwise.

### GetHexcolorOk

`func (o *RouteVisualization) GetHexcolorOk() (*string, bool)`

GetHexcolorOk returns a tuple with the Hexcolor field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHexcolor

`func (o *RouteVisualization) SetHexcolor(v string)`

SetHexcolor sets Hexcolor field to given value.

### HasHexcolor

`func (o *RouteVisualization) HasHexcolor() bool`

HasHexcolor returns a boolean if a field has been set.

### GetPoints

`func (o *RouteVisualization) GetPoints() []GNSSPosition`

GetPoints returns the Points field if non-nil, zero value otherwise.

### GetPointsOk

`func (o *RouteVisualization) GetPointsOk() (*[]GNSSPosition, bool)`

GetPointsOk returns a tuple with the Points field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPoints

`func (o *RouteVisualization) SetPoints(v []GNSSPosition)`

SetPoints sets Points field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


