module Ellmit exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode exposing (field)


type alias LinkListing =
    { links : List Link }


type alias Link =
    { link_id : String
    , title : String
    }


type alias Model =
    { link_listing : Maybe LinkListing }


init : ( Model, Cmd Msg )
init =
    ( Model Nothing
    , Cmd.none
    )


type Msg
    = PleaseFetchLinks
    | DidFetchLinks (Result Http.Error LinkListing)


view : Model -> Html Msg
view model =
    -- this is a good example of my legendary front-end skills
    let
        link_listing =
            case model.link_listing of
                Nothing ->
                    div []
                        [ text "links not fetched yet"
                        , button [ onClick PleaseFetchLinks ] [ text "fetch links!" ]
                        ]

                Just link_listing ->
                    ul []
                        (List.map (\link -> li [] [ text link.title ])
                            link_listing.links
                        )

        --Just links ->
        --    div [] [ text "some links!" ]
    in
        div [] [ link_listing ]


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        PleaseFetchLinks ->
            let
                url =
                    "http://localhost:8080/api/get-best-links"

                request =
                    Http.get url
            in
                ( model, fetchLinks )

        DidFetchLinks (Ok link_listing) ->
            ( { model | link_listing = Just link_listing }, Cmd.none )

        DidFetchLinks (Err _) ->
            Debug.crash "http or decode failure"


fetchLinks : Cmd Msg
fetchLinks =
    let
        url =
            "http://localhost:8080/api/get-best-links"
    in
        Http.send DidFetchLinks (Http.get url decodeLinkListing)


-- generated with http://eeue56.github.io/json-to-elm/ & some tweaks. elm
-- decoders are notoriously annoying to build but the "hard" cases for elmmit
-- are both covered by this one
decodeLinkListing : Json.Decode.Decoder LinkListing
decodeLinkListing =
    Json.Decode.map LinkListing
        (field "links" (Json.Decode.list decodeLink))


decodeLink : Json.Decode.Decoder Link
decodeLink =
    Json.Decode.map2 Link
        (field "link_id" Json.Decode.string)
        (field "title" Json.Decode.string)


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none


main : Program Never Model Msg
main =
    program
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }
