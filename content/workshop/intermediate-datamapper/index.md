---
title: "Perform a data mapping"
date: 2024-12-10T12:00:00+01:00
categories: ["intermediate"]
summary: "Learn how to transform XML data using using the Kaoto DataMapper. We're gonna combine the data from two different sources and create a new Shopping cart XML document."
---
## Overview

The goals for this exercise is to explore how to use the Kaoto DataMapper to transform XML data. We're gonna combine the data from two different sources and create a new Shopping cart XML document.

We're gonna start from [an existing Apache Camel Route (CreateOrder-template)](CreateOrder-template.camel.yaml) that simulates fetching information from external systems, namely [`Account`](xsd/Account.xsd) from `GetAccount` direct route and [`Cart`](xsd/Cart.xsd) from `GetCart` direct route, as well as an order sequence number fetching from `GetOrderSequence` direct route. And then transforming and combining them into a new [`ShipOrder`](xsd/ShipOrder.xsd) format. For this purpose, appropriate XML schemas are provided in the `xsd` folder.

While `Cart` is stored in Camel Message Body, `Account` and order sequence number are stored in Camel Variables. The variable names are `account` and `orderSequence`. In the DataMapper step we will configure later, These Camel Variables are consumed as `Parameters`.

{{<details title="CreateOrder-template.camel.yaml">}}
```yaml
- route:
    id: CreateOrder
    from:
      id: from-9093
      uri: timer
      parameters:
        delay: "1000"
        period: "3000"
        timerName: template
      steps:
        - to:
            id: to-3314
            uri: direct
            parameters:
              name: GetAccount
        - to:
            id: to-2267
            uri: direct
            parameters:
              name: GetCart
        - to:
            id: to-4208
            uri: direct
            parameters:
              name: GetOrderSequence
        - log:
            id: log-1837
            message: ${body}
- route:
    id: GetAccount
    from:
      id: from-1620
      uri: direct
      parameters:
        name: GetAccount
      steps:
        - setVariable:
            id: setVariable-2581
            expression:
              simple:
                expression: >-
                  <kaoto:Account AccountId="acc001"
                  xmlns:kaoto="kaoto.datamapper.test">
                    <Name>Jane Doe</Name>
                    <Address>Purkyňova 111, 612 00</Address>
                    <City>Brno-Medlánky</City>
                    <Country>Česká republika</Country>
                  </kaoto:Account>
            name: account
        - convertVariableTo:
            id: convertVariableTo-3000
            name: account
            type: org.w3c.dom.Document
- route:
    id: GetCart
    from:
      id: "1111"
      uri: direct
      parameters:
        name: GetCart
      steps:
        - setBody:
            id: setBody-3132
            expression:
              simple:
                expression: |-
                  <kaoto:Cart xmlns:kaoto="kaoto.datamapper.test">
                    <Item>
                      <Title>Shadowman T-shirts</Title>
                      <Note>XL</Note>
                      <Quantity>10</Quantity>
                      <Price>25.00</Price>
                    </Item>
                    <Item>
                      <Title>Kaoto T-shirts</Title>
                      <Note>L</Note>
                      <Quantity>5</Quantity>
                      <Price>24.50</Price>
                    </Item>
                  </kaoto:Cart>
        - convertBodyTo:
            id: convertBodyTo-1207
            type: org.w3c.dom.Document
- route:
    id: GetOrderSequence
    from:
      id: from-4065
      uri: direct
      parameters:
        name: GetOrderSequence
      steps:
        - setVariable:
            id: setVariable-2655
            expression:
              simple:
                expression: nnnn
            name: orderSequence

```
{{</details>}}

{{<details title="[Account] object">}}
```xml
<kaoto:Account AccountId="acc001" xmlns:kaoto="kaoto.datamapper.test">
    <Name>Jane Doe</Name>
    <Address>Purkyňova 111, 612 00</Address>
    <City>Brno-Medlánky</City>
    <Country>Česká republika</Country>
</kaoto:Account>
```
{{</details>}}

{{<details title="[Cart] object">}}
```xml
<kaoto:Cart xmlns:kaoto="kaoto.datamapper.test">
    <Item>
        <Title>Shadowman T-shirts</Title>
        <Note>XL</Note>
        <Quantity>10</Quantity>
        <Price>25.00</Price>
    </Item>
    <Item>
        <Title>Kaoto T-shirts</Title>
        <Note>L</Note>
        <Quantity>5</Quantity>
        <Price>24.50</Price>
    </Item>
</kaoto:Cart>
```
{{</details>}}

{{<details title="[ShipOrder] object">}}
```xml
<ShipOrder xmlns="io.kaoto.datamapper.poc.test"
           xmlns:ns0="kaoto.datamapper.test"
           OrderId="ORDER-acc001-nnnn">
   <OrderPerson>acc001:Jane Doe</OrderPerson>
   <ShipTo xmlns="">
      <Name>Jane Doe</Name>
      <Address>Purkyňova 111, 612 00</Address>
      <City>Brno-Medlánky</City>
      <Country>Česká republika</Country>
   </ShipTo>
   <Item xmlns="">
      <Title>Shadowman T-shirts</Title>
      <Note>XL</Note>
      <Quantity>10</Quantity>
      <Price>25.00</Price>
   </Item>
   <Item xmlns="">
      <Title>Kaoto T-shirts</Title>
      <Note>L</Note>
      <Quantity>5</Quantity>
      <Price>24.50</Price>
   </Item>
</ShipOrder>
```
{{</details>}}

## Instructions

- Start with the provided Camel Route [CreateOrder-template](CreateOrder-template.camel.yaml).
- Create a new Kaoto DataMapper step in the route that transforms the data from the `Account`, `Cart`, and `orderSequence` into a new `ShipOrder` format.
- Run the Camel Route and verify that the new `ShipOrder` XML document is printed in the terminal.

## Hints

- Download the provided XML [`Account`](xsd/Account.xsd), [`Cart`](xsd/Cart.xsd) and [`ShipOrder`](xsd/ShipOrder.xsd) schemas to define the structure of the document.
- Append a Kaoto Data Mapper step between the last direct and the log step.
- Configure the Data Mapper step to map the data from the `Account`, `Cart`, and `orderSequence` to the `ShipOrder` format.

{{<details title="Where to apply XSD schemas?">}}
- **account** -> [**Account**](xsd/Account.xsd)
- **orderSequence** -> no schema, just a string
- **Source body** -> [**Cart**](xsd/Cart.xsd)
- **Target body** -> [**ShipOrder**](xsd/ShipOrder.xsd)
{{</details>}}

{{<details title="How to map the data?">}}
1. OrderId -> upper-case(concat('ORD-', $account/Account/@AccountId, '-', $orderSequence))
2. OrderPerson -> concat($account/Account/@AccountId, ':', $account/Account/Name)
3. ShipTo
    - Name -> $account/Account/Name
    - Address -> $account/Account/Address
    - City -> $account/Account/City
    - Country -> $account/Account/Country
4. Item
    - Place a for-each loop over the Cart items.
    - Item -> for-each
    - Title -> Item/Title
    - Note -> Item/Note
    - Quantity -> Item/Quantity
    - Price -> Item/Price
{{</details>}}

## Video walkthrough

{{< youtube iz0yYThHZMc >}}
