cube(`Sales`, {
  sql: `SELECT * FROM fct_sales`,

  measures: {
    totalRevenue: {
      sql: `revenue`,
      type: `sum`,
      format: `currency`
    },

    totalCost: {
      sql: `total_cost`,
      type: `sum`,
      format: `currency`
    },

    totalMargin: {
      sql: `margin`,
      type: `sum`,
      format: `currency`
    },

    totalOrders: {
      sql: `order_id`,
      type: `countDistinct`
    },

    totalQuantity: {
      sql: `quantity`,
      type: `sum`
    },

    averageOrderValue: {
      sql: `${totalRevenue} / NULLIF(${totalOrders}, 0)`,
      type: `number`
    },

    marginRate: {
      sql: `${totalMargin} / NULLIF(${totalRevenue}, 0)`,
      type: `number`
    }
  },

  dimensions: {
    orderId: {
      sql: `order_id`,
      type: `string`,
      primaryKey: true
    },

    orderDate: {
      sql: `order_date`,
      type: `time`
    },

    quarter: {
      sql: `quarter`,
      type: `string`
    },

    region: {
      sql: `region`,
      type: `string`
    },

    country: {
      sql: `country`,
      type: `string`
    },

    productName: {
      sql: `product_name`,
      type: `string`
    },

    category: {
      sql: `category`,
      type: `string`
    },

    customerId: {
      sql: `customer_id`,
      type: `string`
    }
  }
});
